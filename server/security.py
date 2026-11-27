import time
import hmac
import hashlib
import fakeredis
from fastapi import Request, HTTPException

# Khởi tạo Redis giả lập trong bộ nhớ (hoạt động giống hệt Redis thật)
redis_client = fakeredis.FakeStrictRedis(decode_responses=True)

# Kho lưu trữ API Key và Secret Key mẫu
API_KEYS_DB = {
    "client_app_01": "super_secret_key_hutech_b14_2026"
}

# Cấu hình các ngưỡng bảo mật
RATE_LIMIT_MAX_REQUESTS = 5   # Tối đa 5 request
RATE_LIMIT_WINDOW_SEC = 60    # Trong vòng 60 giây
TIMESTAMP_TOLERANCE_SEC = 30  # Cho phép lệch giờ tối đa ±30 giây
NONCE_TTL_SEC = 60            # Lưu Nonce trong Redis 60 giây

def build_canonical_string(method: str, path: str, timestamp: str, nonce: str, body: str) -> str:
    return f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body}"

def generate_hmac_signature(secret_key: str, data: str) -> str:
    return hmac.new(
        key=secret_key.encode("utf-8"),
        msg=data.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

async def verify_full_security(request: Request):
    """Middleware bảo vệ toàn diện: Rate Limit -> Timestamp -> Nonce -> HMAC"""
    api_key = request.headers.get("X-API-Key")
    timestamp_str = request.headers.get("X-Timestamp")
    nonce = request.headers.get("X-Nonce")
    client_signature = request.headers.get("X-Signature")

    # 0. Kiểm tra đủ 4 Header bảo mật
    if not all([api_key, timestamp_str, nonce, client_signature]):
        raise HTTPException(
            status_code=401,
            detail="Thiếu header bắt buộc (X-API-Key, X-Timestamp, X-Nonce, X-Signature)"
        )

    secret_key = API_KEYS_DB.get(api_key)
    if not secret_key:
        raise HTTPException(status_code=401, detail="API Key không hợp lệ")

    # LỚP 1: GIỚI HẠN TẦN SUẤT (RATE LIMITING)
    rate_key = f"ratelimit:{api_key}"
    current_count = redis_client.incr(rate_key)
    if current_count == 1:
        redis_client.expire(rate_key, RATE_LIMIT_WINDOW_SEC)

    if current_count > RATE_LIMIT_MAX_REQUESTS:
        ttl = redis_client.ttl(rate_key)
        raise HTTPException(
            status_code=429,
            detail=f"Vượt quá giới hạn tần suất ({RATE_LIMIT_MAX_REQUESTS} req/{RATE_LIMIT_WINDOW_SEC}s). Thử lại sau {ttl}s.",
            headers={"Retry-After": str(ttl)}
        )

    # LỚP 2: KIỂM TRA DẤU THỜI GIAN (TIMESTAMP)
    try:
        req_timestamp = int(timestamp_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="X-Timestamp phải là số nguyên (Unix timestamp)")

    now = int(time.time())
    if abs(now - req_timestamp) > TIMESTAMP_TOLERANCE_SEC:
        raise HTTPException(
            status_code=401,
            detail=f"Yêu cầu đã hết hạn hoặc sai lệch thời gian quá ±{TIMESTAMP_TOLERANCE_SEC}s (Anti-Replay)"
        )

    # LỚP 3: CHỐNG PHÁT LẠI BẰNG NONCE TRÊN REDIS
    nonce_key = f"nonce:{api_key}:{nonce}"
    if redis_client.exists(nonce_key):
        raise HTTPException(
            status_code=403,
            detail="Phát hiện tấn công phát lại (Replay Attack): Nonce đã được sử dụng!"
        )
    # Lưu Nonce vào Redis để đánh dấu đã dùng
    redis_client.setex(nonce_key, NONCE_TTL_SEC, "used")

    # LỚP 4: XÁC THỰC CHỮ KÝ TOÀN VẸN HMAC-SHA256
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8") if body_bytes else ""

    canonical_data = build_canonical_string(
        method=request.method,
        path=request.url.path,
        timestamp=timestamp_str,
        nonce=nonce,
        body=body_str
    )
    expected_signature = generate_hmac_signature(secret_key, canonical_data)

    if not hmac.compare_digest(expected_signature, client_signature):
        raise HTTPException(
            status_code=401,
            detail="Chữ ký HMAC không khớp! Dữ liệu đã bị thay đổi hoặc sai Secret Key."
        )

    return {
        "api_key": api_key,
        "remaining_quota": RATE_LIMIT_MAX_REQUESTS - current_count
    }