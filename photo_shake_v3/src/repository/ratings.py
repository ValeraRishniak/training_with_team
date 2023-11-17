from typing import Type

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from starlette import status

from src.database.models import Rating, User, Foto, UserRoleEnum
from src.conf import messages as message


async def create_rate(foto_id: int, rate: int, db: Session, user: User) -> Rating:
    """
    The create_rate function creates a new rate for the foto with the given id.
        Args:
            foto_id (int): The id of the foto to be rated.
            rate (int): The rating value, either 1 or - 1.

    :param foto_id: int: Get the foto id from the request
    :param rate: int: Set the rate of the foto
    :param db: Session: Access the database
    :param user: User: Get the user_id of the logged in user
    :return: A rating object
    """
    is_self_foto = db.query(Foto).filter(
        and_(Foto.id == foto_id, Foto.user_id == user.id)).first()
    already_voted = db.query(Rating).filter(and_(Rating.foto_id == foto_id, Rating.user_id == user.id)).first()
    foto_exists = db.query(Foto).filter(Foto.id == foto_id).first()
    if is_self_foto:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=message.OWN_FOTO)
    elif already_voted:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=message.VOTE_TWICE)
    elif foto_exists:
        new_rate = Rating(
            foto_id=foto_id,
            rate=rate,
            user_id=user.id
        )
        db.add(new_rate)
        db.commit()
        db.refresh(new_rate)
        return new_rate


async def edit_rate(rate_id: int, new_rate: int, db: Session, user: User) -> Type[Rating] | None:
    """
    The edit_rate function allows the user to edit a rate.
        Args:
            rate_id (int): The id of the rate that will be edited.
            new_rate (int): The new value for the rating.

    :param rate_id: int: Get the rate id from the database
    :param new_rate: int: Set the new rate value
    :param db: Session: Access the database
    :param user: User: Check if the user is an admin, moderator or the owner of the rate
    :return: The edited rate object
    """
    rate = db.query(Rating).filter(Rating.id == rate_id).first()
    if user.role in [UserRoleEnum.admin, UserRoleEnum.moder] or rate.user_id == user.id:
        if rate:
            rate.rate = new_rate
            db.commit()
    return rate


async def delete_rate(rate_id: int, db: Session, user: User) -> Type[Rating]:
    """
    The delete_rate function deletes a rating from the database.
        Args:
            rate_id (int): The id of the rating to be deleted.
            db (Session): A connection to the database.

    :param rate_id: int: Specify the id of the rate to be deleted
    :param db: Session: Access the database
    :param user: User: Check if the user is logged in
    :return: The deleted rate
    """
    rate = db.query(Rating).filter(Rating.id == rate_id).first()
    if rate:
        db.delete(rate)
        db.commit()
    return rate


async def show_ratings(db: Session, user: User) -> list[Type[Rating]]:
    """
    The show_ratings function returns a list of all ratings in the database.
        Args:
            db (Session): The database session to use for querying.
            user (User): The user making the request.

    :param db: Session: Access the database
    :param user: User: Get the user's id and pass it to the query
    :return: A list of rating objects
    """
    all_ratings = db.query(Rating).all()
    return all_ratings


async def show_my_ratings(db: Session, user: User) -> list[Type[Rating]]:
    """
    The show_ratings function returns a list of all ratings in the database.
        Args:
            db (Session): The database session to use for querying.
            user (User): The user making the request.

    :param db: Session: Access the database
    :param user: User: Get the user's id and pass it to the query
    :return: A list of rating objects
    """
    all_ratings = db.query(Rating).filter(Rating.user_id == user.id).all()
    return all_ratings


async def user_rate_foto(user_id: int, foto_id: int, db: Session, user: User) -> Type[Rating] | None:
    """
    The user_rate_foto function takes in a user_id, foto_id, db and user.
    It then queries the database for any ratings that match both the foto id and the user id.
    If there is a rating it returns it.

    :param user_id: int: Identify the user who is rating the foto
    :param foto_id: int: Get the foto_id from the database
    :param db: Session: Access the database
    :param user: User: Check if the user is logged in or not
    :return: The rating of the user for a specific foto
    """
    user_p_rate = db.query(Rating).filter(and_(Rating.foto_id == foto_id, Rating.user_id == user_id)).first()
    return user_p_rate


