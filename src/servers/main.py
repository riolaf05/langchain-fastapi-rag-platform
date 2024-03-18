from fastapi import FastAPI
from api.subscribe import router
from config import SUBSCRIBER

app = FastAPI(
    title="SNS Subscriber service",
    description="Receives messages from SNS",
)

app.include_router(router, prefix="/subscribe")

@app.on_event("startup")
def start_subscription():
    SUBSCRIBER.create_subscription()


@app.on_event("shutdown")
def end_subscription():
    SUBSCRIBER.delete_subscription()