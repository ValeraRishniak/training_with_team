from datetime import datetime

import pytest

from src.database.models import User, Foto
from src.repository.transform_foto import transform_metod, show_qr
from src.tramsform_schemas import TransformBodyModel


@pytest.fixture()
def new_user(user, session):
    """
    The new_user function takes a user object and a session object as arguments.
    It then queries the database for an existing user with the same email address.
    If no such user exists, it creates one using the information provided in 
    the argument 'user' and adds it to the database.
    
    :param user: Get the email, username and password from the user
    :param session: Query the database for a user with the email address provided
    :return: The new_user object
    """
    new_user = session.query(User).filter(User.email == user.get('email')).first()
    if new_user is None:
        new_user = User(
            email=user.get('email'),
            username=user.get('username'),
            password=user.get('password')
        )  
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return new_user


@pytest.fixture()
def foto(new_user, session):
    """
    The foto function creates a new foto in the database.
        Args:
            new_user (User): The user who created the foto.
            session (Session): A connection to the database.
    
    :param new_user: Create a new user
    :param session: Access the database
    :return: The foto object
    """
    foto = session.query(Foto).first()
    if foto is None:
        foto = Foto(
            image_url="https://res.cloudinary.com/dybgf2pue/image/upload/c_fill,h_250,w_250/Dominic",
            title="cat",
            descr="pet",
            created_at=datetime.now(),
            user_id=new_user.id,
            public_id="Dominic",
            done=True
        )
        session.add(foto)
        session.commit()
        session.refresh(foto)
    return foto


@pytest.fixture()
def body():
    return {
        "circle": {
            "use_filter": True,
            "height": 400,
            "width": 400
        },
        "effect": {
            "use_filter": True,
            "art_audrey": False,
            "art_zorro": True,
            "cartoonify": False,
            "blur": False
        },
        "resize": {
            "use_filter": True,
            "crop": True,
            "fill": False,
            "height": 400,
            "width": 400
        },
        "text": {
            "use_filter": True,
            "font_size": 70,
            "text": "Good"
        },
        "rotate": {
            "use_filter": False,
            "width": 400,
            "degree": 45
        }
    }



@pytest.mark.asyncio
async def test_transform_metod(foto, body, new_user, session):
    """
    The test_transform_metod function tests the transform_metod function.
        Args:
            foto (Foto): A Foto object with a valid id, created by the test_create_foto function.
            body (dict): A dictionary containing all of the necessary information to create a TransformBodyModel object.  This is passed into TransformBodyModel(**body) and then used in transform_metod().  The keys are 'transformation' and 'image'.  The values for these keys are strings that contain Cloudinary transformation parameters and an image URL respectively.  
                Example: {'transformation': &quot;c_thumb
    
    :param foto: Get the foto id from the fixture
    :param body: Pass the body of the request to be tested
    :param new_user: Get the user_id from the database
    :param session: Pass the session object to the function
    :return: A string with the url of the transformed image
    """
    body = TransformBodyModel(**body)
    response = await transform_metod(foto.id, body, new_user, session)
    assert foto.image_url != response.transform_url 


@pytest.mark.asyncio
async def test_show_qr(foto, new_user, session):
    """
    The test_show_qr function tests the show_qr function in views.py
        It does this by creating a new user and foto, then calling the show_qr function with those parameters.
        The response is checked to make sure it's a string.
    
    :param foto: Create a new foto
    :param new_user: Create a new user in the database
    :param session: Create a new session for the user
    :return: A string
    """
    response = await show_qr(foto.id, new_user, session)
    assert isinstance(response, str)
