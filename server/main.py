from fastapi import FastAPI, Depends
from pydantic import BaseModel
from server.security import verify_full_security

app = FastAPI(
    title="API Security Gateway - Đề tài B14",
    description="Hệ thống bảo vệ API: HMAC-SHA256, Anti-Replay (Timestamp + Nonce) và Rate Limiting"
)

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
        "data": payload.model_dump()
    }

# 2. API ĐÃ BẢO VỆ ĐẦY ĐỦ (HMAC + Anti-Replay + Rate Limit)
@app.post("/api/v1/protected/transfer", tags=["2. Protected (Full Security)"])
async def protected_transfer(
    payload: TransferRequest,
    auth_info: dict = Depends(verify_full_security)
):
    return {
        "status": "SUCCESS",
        "mode": "PROTECTED_FULL",
        "verified_client": auth_info["api_key"],
        "remaining_quota_in_minute": auth_info["remaining_quota"],
        "message": f"Giao dịch an toàn! Đã chuyển {payload.amount:,.0f} VND từ {payload.from_account} sang {payload.to_account}",
        "data": payload.model_dump()
    }