import hmac
import hashlib
from fastapi import Request, HTTPException

# Kho lưu trữ API Key và Secret Key mẫu (Trong thực tế lưu ở Database/Vault)
API_KEYS_DB = {
    "client_app_01": "super_secret_key_hutech_b14_2026"
}

def build_canonical_string(method: str, path: str, timestamp: str, nonce: str, body: str) -> str:
    """
    Tạo chuỗi chuẩn hóa (Canonical String) trước khi băm HMAC.
    Quy ước chung giữa Client và Server:
    METHOD + \n + URI_PATH + \n + TIMESTAMP + \n + NONCE + \n + BODY
    """
    return f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body}"

def generate_hmac_signature(secret_key: str, data: str) -> str:
    """Tạo chữ ký HMAC-SHA256 dạng chuỗi thập lục phân (hex)"""
    return hmac.new(
        key=secret_key.encode("utf-8"),
        msg=data.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

async def verify_hmac_only(request: Request):
    """Middleware kiểm tra định danh API Key và chữ ký toàn vẹn HMAC-SHA256"""
    api_key = request.headers.get("X-API-Key")
    timestamp = request.headers.get("X-Timestamp", "")
    nonce = request.headers.get("X-Nonce", "")
    client_signature = request.headers.get("X-Signature")

    # 1. Kiểm tra sự tồn tại của Header bắt buộc
    if not api_key or not client_signature:
        raise HTTPException(status_code=401, detail="Thiếu header X-API-Key hoặc X-Signature")

    # 2. Kiểm tra API Key có hợp lệ không
    secret_key = API_KEYS_DB.get(api_key)
    if not secret_key:
        raise HTTPException(status_code=401, detail="API Key không hợp lệ")

    # 3. Đọc nội dung Body của request
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8") if body_bytes else ""

    # 4. Tái tạo chuỗi chuẩn hóa và tự tính chữ ký phía Server
    canonical_data = build_canonical_string(
        method=request.method,
        path=request.url.path,
        timestamp=timestamp,
        nonce=nonce,
        body=body_str
    )
    expected_signature = generate_hmac_signature(secret_key, canonical_data)

    # 5. So sánh an toàn hằng thời gian (chống Timing Attack)
    if not hmac.compare_digest(expected_signature, client_signature):
        raise HTTPException(
            status_code=401,
            detail="Chữ ký HMAC không khớp! Dữ liệu đã bị sửa đổi hoặc sai khóa bí mật."
        )

    return {"api_key": api_key, "status": "verified"}