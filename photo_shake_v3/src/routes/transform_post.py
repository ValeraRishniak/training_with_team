from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.conf.messages import NOT_FOUND
from src.database.connect_db import get_db
from src.database.models import User
from src.schemas import FotoResponse
from src.services.auth import auth_service
from src.tramsform_schemas import TransformBodyModel
from src.repository import transform_foto as transform_foto

router = APIRouter(prefix='/transformations', tags=["transformations"])


@router.patch("/{foto_id}", response_model=FotoResponse, status_code=status.HTTP_200_OK)
async def transform_metod(foto_id: int, body: TransformBodyModel, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The transform_metod function takes a foto_id and body as input,
        and returns the transformed foto.
    
    :param foto_id: int: Get the foto id from the url
    :param body: TransformBodyModel: Get the data from the body of the request
    :param db: Session: Get the database session
    :param current_user: User: Get the user id of the current user
    :return: A foto with a new body and title
    """
    foto = await transform_foto.transform_metod(foto_id, body, current_user, db)
    if foto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return foto


@router.post("/qr/{foto_id}", status_code=status.HTTP_200_OK)
async def show_qr(foto_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The show_qr function returns a QR code for the foto with the given id.
        The user must be logged in to view this page.
    
    :param foto_id: int: Find the foto that is being updated
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: A foto object
    """
    foto = await transform_foto.show_qr(foto_id, current_user, db)
    if foto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return foto
