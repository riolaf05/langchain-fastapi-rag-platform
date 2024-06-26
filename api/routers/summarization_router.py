from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette import status
from services.summarization_service import SummarizationService

from models.serializers import ReceiverSerializer

router = APIRouter()

summarization_service = SummarizationService()


@router.get("/healthcheck", operation_id="subscribe/healthcheck")
async def health():
    response = JSONResponse(content="OK!", status_code=status.HTTP_200_OK)
    return response


@router.post("/summarization", operation_id="subscribe/summarization")
async def receive_message(request: Request, receiver_data: ReceiverSerializer):
    success = summarization_service.process(**receiver_data.model_dump())

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
