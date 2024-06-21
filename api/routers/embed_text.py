from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette import status
from services.text_service import TextService

from models.serializers import ReceiverSerializer

router = APIRouter()

text_service = TextService()

@router.post("/text-input")
async def receive_message(request: Request, receiver_data: ReceiverSerializer):
    success = text_service.process(**receiver_data.dict())

    if success:
        response = JSONResponse(
            content={"message": "Message received!"},
            status_code=status.HTTP_200_OK
        )
    else:
        response = JSONResponse(
            content={"message": "ERROR"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response