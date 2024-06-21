from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette import status
from services.embedding_service import EmbeddingService

from models.serializers import ReceiverSerializer

router = APIRouter()

embedding_service = EmbeddingService()


@router.post("/embedding", operation_id="subscribe/embedding")
async def receive_message(request: Request, receiver_data: ReceiverSerializer):
    success = embedding_service.process(**receiver_data.model_dump())

    if success:
        response = JSONResponse(
            content={"message": "Message received!"}, status_code=status.HTTP_200_OK
        )
    else:
        response = JSONResponse(
            content={"message": "ERROR"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
