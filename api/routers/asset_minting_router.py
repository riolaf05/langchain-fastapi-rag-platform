from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette import status

from services.asset_minting_service import AssetMintingService

router = APIRouter()
asset_minting_service = AssetMintingService()

@router.post("/mint-assets")
async def mint_assets():
    """
    Endpoint to mint assets.
    Returns:
        JSONResponse: Response indicating the success or failure of asset minting.
    """
    success = asset_minting_service.mint_assets()

    if success:
        response = JSONResponse(
            content={"message": "Assets minted successfully!"},
            status_code=status.HTTP_200_OK
        )
    else:
        response = JSONResponse(
            content={"message": "Failed to mint assets. Please check your request."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
