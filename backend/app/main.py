from fastapi import FastAPI

app = FastAPI(title="QueryECE API")

@app.get("/")
def read_root():
    return {"status": "Backend is running"}