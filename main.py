from uvicorn import run
from fastapi import FastAPI
from api.routers import upload_router, summarization_router, asset_minting_router


app = FastAPI(
    title="SNS Subscriber service",
    description="Receives messages from SNS",
    redoc_url="/redoc"
)

# Include routers for API endpoints
app.include_router(summarization_router.router, prefix="/subscribe") #the prefix subscribe is used to mark the endpoint served by SNS 
app.include_router(asset_minting_router.router, prefix="/subscribe")
app.include_router(upload_router.router)


if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=3000, reload=True)