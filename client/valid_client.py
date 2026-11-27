import time
import uuid
import json
import hmac
import hashlib
import requests

BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/protected/transfer"
API_KEY = "client_app_01"
SECRET_KEY = "super_secret_key_hutech_b14_2026"

def send_signed_request(from_acc: str, to_acc: str, amount: float, note: str):
    payload = {
        "from_account": from_acc,
        "to_account": to_acc,
        "amount": amount,
        "note": note
    }
    # Chuyển dictionary thành chuỗi JSON chuẩn (không khoảng trắng thừa)
    body_str = json.dumps(payload, separators=(",", ":"))
    
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    
    # Tạo chuỗi chuẩn hóa và ký HMAC-SHA256
    canonical_data = f"POST\n{ENDPOINT}\n{timestamp}\n{nonce}\n{body_str}"
    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        canonical_data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature
    }

    response = requests.post(BASE_URL + ENDPOINT, data=body_str, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}\n")

if __name__ == "__main__":
    print("--- Gửi 6 request liên tiếp để kiểm tra luồng hợp lệ và ngưỡng Rate Limit (5 req/phút) ---")
    for i in range(1, 7):
        print(f"Lần gửi thứ {i}:")
        send_signed_request("100123456", "999888777", 500000 * i, f"Chuyen khoan lan {i}")