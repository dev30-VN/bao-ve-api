from fastapi import FastAPI

app = FastAPI(title="Bảo Vệ API")

@app.get("/")
def read_root():
    return {"message": "Dự án bao-ve-api đã khởi chạy thành công!"}