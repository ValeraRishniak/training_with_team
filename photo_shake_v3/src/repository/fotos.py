from typing import List
from datetime import datetime

import cloudinary
import cloudinary.uploader

from fastapi import Request, UploadFile
from faker import Faker
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from src.conf.config import init_cloudinary
from src.database.models import Foto, Tag, User, Comment, UserRoleEnum
from src.schemas import FotoUpdate


async def create_foto(
    request: Request,
    title: str,
    descr: str,
    tags: List,
    file: UploadFile,
    db: Session,
    current_user: User,
) -> Foto:
    """
    The create_foto function creates a new foto in the database.

    :param request: Request: Get the request object, which contains information about the incoming http request
    :param title: str: Get the title of the foto from the request
    :param descr: str: Get the description of the foto
    :param tags: List: Get the tags from the request body
    :param file: UploadFile: Get the file from the request and upload it to cloudinary
    :param db: Session: Access the database
    :param current_user: User: Get the user_id of the current user
    :return: A foto object
    """
    # me = db.query(User).filter(User.id == user.id).first()
    # if new_username:
    #     me.username = new_username

    # public_id = Faker().first_name() # треба списати цей параметр
    # public_id = f'{current_user}'

    photo_number = 1

    db_photo = (
        db.query(Foto)
        .filter(and_(Foto.user_id == current_user.id, Foto.id == photo_number))
        .first()
    )

    if db_photo:
        photo_number += 1

    public_id = f"PhotoShake/{photo_number}"

    init_cloudinary()
    cloudinary.uploader.upload(file.file, public_id=public_id)
    # url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill')
    url = cloudinary.CloudinaryImage(f"PhotoShake/{photo_number}").build_url(
        width=250, height=250, crop="fill"
    )
    url2 = url
    # print(url)
    # cloudinary.uploader.upload(url)
    # https://res.cloudinary.com/dpkgielju/image/upload/c_fill,h_250,w_250/v1/PhotoShake/teamlead
    # https://res.cloudinary.com/dpkgielju/image/upload/v1700173065/Gregory.jpg

    if tags:
        tags = get_tags(tags[0].split(","), current_user, db)
    """
    cloudinary.uploader.upload("https://upload.wikimedia.org/wikipedia/commons/a/ae/Olympic_flag.jpg", 
    public_id = "olympic_flag")
    """
    foto = Foto(
        image_url=url,
        transform_url=url2,
        title=title,
        descr=descr,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        tags=tags,
        done=True,
        user_id=current_user.id,
        public_id=public_id,
    )
    db.add(foto)
    db.commit()
    db.refresh(foto)
    # return url
    return foto


async def get_all_fotos(skip: int, limit: int, db: Session) -> List[Foto]:
    """
    The get_all_fotos function returns a list of all fotos in the database.

    :param skip: int: Skip a certain number of fotos
    :param limit: int: Limit the number of fotos returned
    :param db: Session: Pass the database session to the function
    :return: A list of all fotos in the database
    """
    return db.query(Foto).offset(skip).limit(limit).offset(skip).limit(limit).all()


async def get_my_fotos(skip: int, limit: int, user: User, db: Session) -> List[Foto]:
    """
    The get_my_fotos function returns a list of fotos for the user.

    :param skip: int: Skip a number of fotos
    :param limit: int: Limit the number of fotos returned
    :param user: User: Get the fotos of a specific user
    :param db: Session: Pass the database session to the function
    :return: A list of fotos
    """
    return (
        db.query(Foto).filter(Foto.user_id == user.id).offset(skip).limit(limit).all()
    )


async def get_foto_by_id(foto_id: int, user: User, db: Session) -> Foto:
    """
    The get_foto_by_id function returns a foto object from the database based on the user and foto id.
        Args:
            foto_id (int): The id of the desired Foto object.
            user (User): The User who owns this Foto.
            db (Session): A connection to our database session, used for querying data from it.

    :param foto_id: int: Specify the id of the foto that is being retrieved
    :param user: User: Get the user id from the database
    :param db: Session: Pass the database session to the function
    :return: The foto object that has the id of the foto_id parameter
    """
    foto = (
        db.query(Foto).filter(and_(Foto.user_id == user.id, Foto.id == foto_id)).first()
    )
    return foto


async def get_fotos_by_title(foto_title: str, user: User, db: Session) -> List[Foto]:
    """
    The get_fotos_by_title function returns a list of fotos that match the given title.


    :param foto_title: str: Get the foto title from the user
    :param user: User: Get the user id from the jwt token
    :param db: Session: Pass the database session to the function
    :return: A list of fotos that match the foto title
    """
    return (
        db.query(Foto)
        .filter(func.lower(Foto.title).like(f"%{foto_title.lower()}%"))
        .all()
    )


async def get_fotos_by_user_id(user_id: int, db: Session) -> List[Foto]:
    """
    The get_fotos_by_user_id function returns a list of fotos by user_id.

    :param user_id: int: Specify the type of data that is expected to be passed in
    :param db: Session: Pass in the database session
    :return: A list of foto objects
    """
    return db.query(Foto).filter(Foto.user_id == user_id).all()


async def get_fotos_by_username(user_name: str, db: Session) -> List[Foto]:
    """
    The get_fotos_by_username function takes in a user_name and db Session object,
        then returns a list of Foto objects that match the given username.


    :param user_name: str: Specify the username of the user whose fotos we want to get
    :param db: Session: Access the database
    :return: A list of fotos by the username provided
    """
    searched_user = (
        db.query(User)
        .filter(func.lower(User.username).like(f"%{user_name.lower()}%"))
        .first()
    )
    if searched_user:
        return db.query(Foto).filter(Foto.user_id == searched_user.id).all()


async def get_fotos_with_tag(tag_name: str, db: Session) -> List[Foto]:
    """
    The get_fotos_with_tag function returns a list of fotos that have the given tag.
        Args:
            tag_name (str): The name of the desired tag.
            db (Session): A database session object to query from.

    :param tag_name: str: Specify the tag that we want to search for
    :param db: Session: Pass the database session to the function
    :return: A list of foto objects that have the given tag
    """
    return db.query(Foto).join(Foto.tags).filter(Tag.title == tag_name).all()


async def get_foto_comments(foto_id: int, db: Session) -> List[Comment]:
    """
    The get_foto_comments function returns a list of comments for the specified foto_id.
        Args:
            foto_id (int): The id of the Foto to retrieve comments for.
            db (Session): A database session object used to query the database.
        Returns:
            List[Comment]: A list of Comment objects that are associated with the specified Foto.

    :param foto_id: int: Filter the comments by foto_id
    :param db: Session: Pass the database session to the function
    :return: A list of comments for a given foto
    """
    return db.query(Comment).filter(Comment.foto_id == foto_id).all()


def get_tags(tag_titles: list, user: User, db: Session):
    """
    The get_tags function takes a list of tag titles and returns a list of Tag objects.
    If the tag does not exist in the database, it is created.

    :param tag_titles: list: Pass in a list of tag titles
    :param user: User: Get the user id for the tag
    :param db: Session: Query the database for a tag
    :return: A list of tags
    """
    tags = []
    for tag_title in tag_titles:
        tag = db.query(Tag).filter(Tag.title == tag_title).first()
        if not tag:
            tag = Tag(
                title=tag_title,
                user_id=user.id,
            )
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tags.append(tag)
    return tags


async def get_foto_by_keyword(keyword: str, db: Session):
    """
    The get_foto_by_keyword function returns a list of fotos that match the keyword.
        The keyword is searched in both the title and description fields.

    :param keyword: str: Filter the fotos by title or description
    :param db: Session: Pass the database session to the function
    :return: A list of foto objects
    """
    return (
        db.query(Foto)
        .filter(
            or_(
                func.lower(Foto.title).like(f"%{keyword.lower()}%"),
                func.lower(Foto.descr).like(f"%{keyword.lower()}%"),
            )
        )
        .all()
    )


async def update_foto(
    foto_id: int, body: FotoUpdate, user: User, db: Session
) -> Foto | None:
    """
    The update_foto function updates a foto in the database.

    :param foto_id: int: Identify the foto to update
    :param body: FotoUpdate: Get the title, description and tags from the request body
    :param user: User: Check if the user is an admin or not
    :param db: Session: Connect to the database
    :return: The updated foto
    """
    foto = db.query(Foto).filter(Foto.id == foto_id).first()

    if foto:
        if user.role == UserRoleEnum.admin or foto.user_id == user.id:
            tags = []
            if body.tags:
                tags = get_tags(body.tags, user, db)

            foto.title = body.title
            foto.descr = body.descr
            foto.tags = tags
            foto.updated_at = datetime.now()
            foto.done = True
            db.commit()
    return foto


async def remove_foto(foto_id: int, user: User, db: Session) -> Foto | None:
    """
    The remove_foto function removes a foto from the database.
        Args:
            foto_id (int): The id of the foto to be removed.
            user (User): The user who is removing the foto.
            db (Session): A database session object for interacting with the database.
        Returns:
            Foto | None: If successful, returns a Foto object representing what was removed from
                the database; otherwise, returns None if no such Foto exists in the first place.

    :param foto_id: int: Specify the id of the foto to be removed
    :param user: User: Check if the user is an admin or if they are the owner of the foto
    :param db: Session: Access the database
    :return: The foto that was removed
    """
    foto = db.query(Foto).filter(Foto.id == foto_id).first()
    if foto:
        if user.role == UserRoleEnum.admin or foto.user_id == user.id:
            init_cloudinary()
            cloudinary.uploader.destroy(foto.public_id)
            db.delete(foto)
            db.commit()
    return foto
