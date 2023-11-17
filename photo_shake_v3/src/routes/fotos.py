from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Request
from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.connect_db import get_db
from src.database.models import User, UserRoleEnum
from src.schemas import CommentModel, FotoModel, FotoResponse, FotoUpdate
from src.repository import fotos as repository_fotos
from src.services.auth import auth_service
from src.conf.messages import NOT_FOUND
from src.services.roles import RoleChecker
# from src.services.roles import RoleChecker

router = APIRouter(prefix='/fotos', tags=["fotos"])

# для визначення дозволу в залежності від ролі добавляємо списки дозволеності
allowed_get_all_fotos = RoleChecker([UserRoleEnum.admin])


@router.post("/new/", response_model=FotoResponse, status_code=status.HTTP_201_CREATED)
async def create_foto(request: Request,
                    title: str = Form(), descr: str = Form(),
                    tags: List = Form(None), file: UploadFile = File(None),
                    db: Session = Depends(get_db), 
                    current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_foto function creates a new foto in the database.
        The function takes in a title, description, tags and an image file as parameters.
        It then uses these to create a new foto object which is added to the database.
    
    :param request: Request: Get the request object
    :param title: str: Get the title of the foto from the request body
    :param descr: str: Get the description of the foto from the request
    :param tags: List: Get the list of tags from the request body
    :param file: UploadFile: Get the file from the request
    :param db: Session: Get the database session, which is used to perform sql queries
    :param current_user: User: Get the user who is currently logged in
    :return: A dict, which is a json object
    """
    return await repository_fotos.create_foto(request, title, descr, tags, file, db, current_user)











@router.get("/my_fotos", response_model=List[FotoResponse])
async def read_all_user_fotos(skip: int = 0, limit: int = 100, current_user: User = Depends(auth_service.get_current_user), 
                              db: Session = Depends(get_db)):
    """
    The read_all_user_fotos function returns all fotos for a given user.
        The function takes in the following parameters:
            skip (int): The number of fotos to skip before returning results. Default is 0.
            limit (int): The maximum number of fotos to return per page. Default is 100, max is 1000.
    
    :param skip: int: Skip a number of fotos
    :param limit: int: Limit the number of fotos returned
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A list of fotos
    """
    fotos = await repository_fotos.get_my_fotos(skip, limit, current_user, db)
    if fotos is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return fotos


@router.get("/all", response_model=List[FotoResponse], dependencies=[Depends(allowed_get_all_fotos)])
async def read_all_fotos(skip: int = 0, limit: int = 100,
            current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The read_all_fotos function returns all fotos in the database.
        ---
        get:
          summary: Returns all fotos in the database.
          description: Returns a list of all fotos in the database, with optional skip and limit parameters to paginate results.
          tags: [fotos]
          responses:
            '200': # HTTP status code 200 is returned when successful (OK) 
    
    :param skip: int: Skip the first n fotos
    :param limit: int: Limit the number of fotos returned
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A list of fotos
    """
    fotos = await repository_fotos.get_all_fotos(skip, limit, db)
    if fotos is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return fotos


@router.get("/by_id/{foto_id}", response_model=FotoResponse)
async def read_foto_by_id(foto_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_foto_by_id function returns a foto by its id.
        If the user is not logged in, it will return an error message.
        If the user is logged in but does not have access to this foto, it will return an error message.
    
    :param foto_id: int: Get the foto by id
    :param db: Session: Pass the database session to the function
    :param current_user: User: Check if the user is authorized to access the foto
    :return: A foto object, as defined in the models
    """
    foto = await repository_fotos.get_foto_by_id(foto_id, current_user, db)
    if foto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return foto


@router.get("/by_title/{foto_title}", response_model=List[FotoResponse])
async def read_fotos_with_title(foto_title: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_fotos_with_title function is used to read fotos with a given title.
        The function takes in the foto_title as an argument and returns all fotos that match the title.
    
    :param foto_title: str: Pass the title of the foto to be searched for
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user, and the db: session parameter is used to get a database session
    :return: A list of fotos
    """
    fotos = await repository_fotos.get_fotos_by_title(foto_title, current_user, db)
    if not fotos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return fotos


@router.get("/by_user_id/{user_id}", response_model=List[FotoResponse])
async def read_fotos_by_user_id(user_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_fotos_by_user_id function returns all fotos by a user with the given id.
        The function takes in an integer user_id and returns a list of foto objects.
    
    :param user_id: int: Specify the user_id of the fotos that we want to retrieve
    :param db: Session: Pass the database connection to the repository
    :param current_user: User: Get the user that is currently logged in
    :return: A list of fotos
    """
    fotos = await repository_fotos.get_fotos_by_user_id(user_id, db)
    if not fotos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return fotos


@router.get("/by_username/{user_name}", response_model=List[FotoResponse])
async def read_foto_with_user_username(user_name: str, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_foto function is used to read a foto by username.
        The function takes in the user_name and db as parameters,
        and returns fotos.
    
    :param user_name: str: Get the username of the user whose fotos we want to read
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A list of fotos, which is the same as what i am trying to return in my test
    """
    fotos = await repository_fotos.get_fotos_by_username(user_name, db)
    if not fotos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return fotos


@router.get("/with_tag/{tag_name}", response_model=List[FotoResponse])
async def read_foto_with_tag(tag_name: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_foto_with_tag function returns a list of fotos that contain the tag_name.
        The function takes in a tag_name and an optional db Session object, which is used to connect to the database.
        It also takes in an optional current_user User object, which is used for authentication purposes.
    
    :param tag_name: str: Get the tag name from the url path
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: A list of fotos that contain the tag
    """
    fotos = await repository_fotos.get_fotos_with_tag(tag_name, db)
    if not fotos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return fotos


@router.get("/comments/all/{foto_id}", response_model=List[CommentModel])
async def read_foto_comments(foto_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_foto_comments function returns a list of comments for the specified foto.
        The function takes in an integer representing the foto_id and returns a list of comments.
    
    :param foto_id: int: Get the foto_id from the url
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user details of the current logged in user
    :return: A list of comments for a foto
    """
    fotos = await repository_fotos.get_foto_comments(foto_id, db)
    if not fotos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return fotos


@router.get("/by_keyword/{keyword}", response_model=List[FotoResponse])
async def read_fotos_by_keyword(keyword: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_foto_by_keyword function returns a list of fotos that contain the keyword in their title or body.
    
    :param keyword: str: Specify the keyword that we want to search for
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user who is logged in
    :return: A list of fotos
    """
    fotos = await repository_fotos.get_foto_by_keyword(keyword, db)
    if not fotos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return fotos

@router.put("/{foto_id}", response_model=FotoResponse)
async def update_foto(body: FotoUpdate, foto_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_foto function updates a foto in the database.
        The function takes three arguments:
            - body: A fotoUpdate object containing the new values for the foto.
            - foto_id: An integer representing the id of an existing foto to update.
            - db (optional): A Session object used to connect to and query a database, defaults to None if not provided. 
                If no session is provided, one will be created using get_db().
    
    :param body: FotoUpdate: Get the data from the request body
    :param foto_id: int: Find the foto in the database
    :param db: Session: Pass the database session to the repository
    :param current_user: User: Check if the user is authorized to update the foto
    :return: A foto object
    """
    foto = await repository_fotos.update_foto(foto_id, body, current_user, db)
    if foto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return foto


@router.delete("/{foto_id}", response_model=FotoResponse)
async def remove_foto(foto_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_foto function removes a foto from the database.
        The function takes in an integer representing the id of the foto to be removed,
        and returns a dictionary containing information about that foto.
    
    :param foto_id: int: Specify the foto to be deleted
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Check if the user is logged in
    :return: A foto object, but the remove_foto function in repository_fotos returns none
    """
    foto = await repository_fotos.remove_foto(foto_id, current_user, db)
    if foto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return foto














