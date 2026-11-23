from fastapi import FastAPI, Depends
from pydantic import BaseModel
from server.security import verify_hmac_only

app = FastAPI(
    title="API Security Gateway - Đề tài B14",
    description="Hệ thống minh họa bảo vệ API: HMAC Signature, Anti-Replay và Rate Limiting"
)

# Mô hình dữ liệu giao dịch chuyển khoản mẫu
class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float
    note: str = ""

# 1. API GỐC CHƯA BẢO VỆ (Baseline)
@app.post("/api/v1/unprotected/transfer", tags=["1. Unprotected (Baseline)"])
async def unprotected_transfer(payload: TransferRequest):
    return {
        "status": "SUCCESS",
        "mode": "UNPROTECTED",
        "message": f"Đã chuyển {payload.amount:,.0f} VND từ {payload.from_account} sang {payload.to_account}",
        "data": payload.dict()
    }

# 2. API ĐÃ BẢO VỆ BẰNG CHỮ KÝ HMAC
@app.post("/api/v1/protected/transfer", tags=["2. Protected (HMAC)"])
async def protected_transfer(
    payload: TransferRequest,
    auth_info: dict = Depends(verify_hmac_only)
):
    return {
        "status": "SUCCESS",
        "mode": "PROTECTED_HMAC",
        "verified_client": auth_info["api_key"],
        "message": f"Giao dịch hợp lệ! Đã chuyển {payload.amount:,.0f} VND từ {payload.from_account} sang {payload.to_account}",
        "data": payload.dict()
    }