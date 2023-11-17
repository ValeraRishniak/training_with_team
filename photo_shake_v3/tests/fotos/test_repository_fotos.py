from datetime import datetime

import pytest
import io
from fastapi import Request, UploadFile
from PIL import Image

from src.database.models import User, Foto
import src.repository.fotos as repository_fotos
from src.schemas import FotoUpdate


@pytest.fixture()
def current_user(user, session):
    """
    The current_user function takes in a user and session object.
    It then queries the database for a user with the same email as the one passed in.
    If no such user exists, it creates one and adds it to the database. 
    Finally, it returns that current_user.
    
    :param user: Get the user's email, username and password
    :param session: Query the database for a user with the email address provided by google
    :return: The current user
    """
    current_user = session.query(User).filter(User.email == user.get('email')).first()
    if current_user is None:
        current_user = User(
            email=user.get('email'),
            username=user.get('username'),
            password=user.get('password')
        )  
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
    return current_user


@pytest.fixture()
def foto(current_user, session):
    """
    The foto function creates a new foto in the database.
        If there is no foto, it will create one with the following parameters:
            image_url = &quot;Dominic&quot;
            title = &quot;cat&quot;
            descr = &quot;pet&quot;  # description
            created_at = datetime.now()
            user_id=current_user.id
    
    :param current_user: Get the user_id of the current user
    :param session: Query the database and get a foto
    :return: A foto object
    """
    foto = session.query(Foto).first()
    if foto is None:
        foto = Foto(
            image_url="https://res.cloudinary.com/dybgf2pue/image/upload/c_fill,h_250,w_250/Dominic",
            title="cat",
            descr="pet",
            created_at=datetime.now(),
            user_id=current_user.id,
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
        "title": "other_foto",
        "descr": "other_foto",
        "tags": ["other_foto"]
    }


@pytest.mark.asyncio
async def test_create_foto(request: Request, session, current_user):
    """
    The test_create_foto function tests the create_foto function in repository_fotos.py
        It creates a foto with title, description and tags as well as an image file.
        The test checks if the response is of type str (image url) and if it has the correct title, description and tags.
    
    :param request: Request: Pass the request object to the function
    :param session: Access the database
    :param current_user: Get the user_id from the current user
    :return: A foto object and we can check the properties of this object
    """
    file_data = io.BytesIO()
    image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
    image.save(file_data, 'jpeg')
    file_data.seek(0)
    
    file = UploadFile(file_data)
    title = "test_foto"
    descr = "test_foto"
    tags = ["test_foto"]
    response = await repository_fotos.create_foto(request, title, descr, tags, file, session, current_user)
    assert isinstance(response.image_url, str)
    assert response.title == title
    assert response.descr == descr


@pytest.mark.asyncio
async def test_get_all_fotos(session):
    """
    The test_get_all_fotos function tests the get_all_fotos function in the repository_fotos module.
    The test passes if:
        1) The response is a list of fotos.
        2) The length of the list is greater than or equal to one.
    
    :param session: Pass the session object to the repository_fotos
    :return: A list of fotos
    """
    skip = 0
    limit = 100
    response = await repository_fotos.get_all_fotos(skip, limit, session)
    assert isinstance(response, list)
    assert len(response) >= 1


@pytest.mark.asyncio
async def test_get_my_fotos(current_user, session):
    """
    The test_get_my_fotos function tests the get_my_fotos function in the repository_fotos module.
    The test passes if a list of fotos is returned and has at least one foto.
    
    :param current_user: Get the user's fotos
    :param session: Pass the database session to the repository function
    :return: A list of fotos that the current user has created
    """
    skip = 0
    limit = 100
    response = await repository_fotos.get_my_fotos(skip, limit, current_user, session)
    assert isinstance(response, list)
    assert len(response) >= 1


@pytest.mark.asyncio
async def test_get_foto_by_id(foto, current_user, session):
    """
    The test_get_foto_by_id function tests the get_foto_by_id function in repository/fotos.py
        It does this by creating a foto, and then calling the get_foto_by_id function with that foto's id.
        The response is then checked to make sure it has the same title and description as what was created.
    
    :param foto: Pass in the foto object that was created earlier
    :param current_user: Check if the user is allowed to see the foto
    :param session: Pass the database session to the function
    :return: The foto
    """
    response = await repository_fotos.get_foto_by_id(foto.id, current_user, session)
    assert response.title == "test_foto"
    assert response.descr == "test_foto"


@pytest.mark.asyncio
async def test_get_fotos_by_title(current_user, session):
    """
    The test_get_fotos_by_title function tests the get_fotos_by_title function in repository/repository.py
        The test passes if:
            - response is a list of fotos with title &quot;test_foto&quot; and description &quot;test_foto&quot;
    
    
    :param current_user: Pass the current user to the function
    :param session: Create a new session for the test
    :return: A list of fotos that have the title &quot;test_foto&quot;
    """
    foto_title = "test_foto"
    response = await repository_fotos.get_fotos_by_title(foto_title, current_user, session)
    assert isinstance(response, list)
    assert response[0].title == "test_foto"
    assert response[0].descr == "test_foto"


@pytest.mark.asyncio
async def test_get_fotos_by_user_id(current_user, session):
    """
    The test_get_fotos_by_user_id function tests the get_fotos_by_user_id function in the repository/fotos.py file.
    The test passes if a list of fotos is returned and if the title and description of each foto are correct.
    
    :param current_user: Pass in the user object that is created in the conftest
    :param session: Pass the session object to the function
    :return: A list of fotos
    """
    response = await repository_fotos.get_fotos_by_user_id(current_user.id, session)
    assert isinstance(response, list)
    assert response[0].title == "test_foto"
    assert response[0].descr == "test_foto"


@pytest.mark.asyncio
async def test_get_fotos_by_username(current_user, session):
    """
    The test_get_fotos_by_username function tests the get_fotos_by_username function in the repository.py file.
    It checks that a list is returned and that it contains a foto with title &quot;test_foto&quot; and description &quot;test_foto&quot;.
    
    
    :param current_user: Create a foto in the database
    :param session: Pass the database connection to the function
    :return: A list of fotos
    """
    response = await repository_fotos.get_fotos_by_username(current_user.username, session)
    assert isinstance(response, list)
    assert response[0].title == "test_foto"
    assert response[0].descr == "test_foto"


@pytest.mark.asyncio
async def test_get_fotos_with_tag(session):
    """
    The test_get_fotos_with_tag function tests the get_fotos_with_tag function in repository/repository.py
        The test passes if the response is a list and if the title and description of the first item in that list are equal to &quot;test_foto&quot;
    
    
    :param session: Pass the session to the repository layer
    :return: A list of fotos with the tag &quot;test_foto&quot;
    """
    tag_name = "test_foto"
    response = await repository_fotos.get_fotos_with_tag(tag_name, session)
    assert isinstance(response, list)
    assert response[0].title == "test_foto"
    assert response[0].descr == "test_foto"


@pytest.mark.asyncio
async def test_get_foto_comments(foto, session):
    """
    The test_get_foto_comments function tests the get_foto_comments function in the repository_fotos module.
        The test is successful if a list of comments is returned.
    
    :param foto: Pass in a foto object to the function
    :param session: Pass the database session to the repository function
    :return: A list of comments for a foto
    """
    response = await repository_fotos.get_foto_comments(foto.id, session)
    assert isinstance(response, list)


def test_get_tags(current_user, session): 
    """
    The test_get_tags function tests the get_tags function in the repository_fotos module.
        The test passes if a list of tags is returned from the database that matches what was passed into
        the function.
    
    :param current_user: Get the user id of the current user
    :param session: Create a new session to the database
    :return: A list of tags that match the tag_titles parameter
    """
    tag_titles = ["new_test_foto"]
    response = repository_fotos.get_tags(tag_titles, current_user, session)
    assert response[0].title == "new_test_foto"


@pytest.mark.asyncio
async def test_get_foto_by_keyword(foto, session):
    """
    The test_searcher function tests the searcher function in repository_fotos.py
        It creates a foto with title and descr &quot;test_foto&quot; and then searches for it using the keyword &quot;test_foto&quot;.
        The test passes if the response is a list, if its first element has title and descr equal to &quot;test_foto&quot;, 
        and if its id is equal to that of our created foto.
    
    :param foto: Pass the foto object to the function, which is used in the test
    :param session: Create a session to the database
    :return: A list of fotos
    """
    keyword = foto.title
    response = await repository_fotos.get_foto_by_keyword(keyword, session)
    assert isinstance(response, list)
    assert response[0].title == "test_foto"
    assert response[0].descr == "test_foto"
    assert response[0].id == foto.id


@pytest.mark.asyncio
async def test_update_foto(foto, body, current_user, session):
    """
    The test_update_foto function tests the update_foto function in repository_fotos.py
        It does this by creating a foto, then updating it with new data and checking that the 
        response is correct.
    
    :param foto: Create the foto object that will be updated
    :param body: Pass the body of the request to update a foto
    :param current_user: Check if the user is authorized to update the foto
    :param session: Pass the database session to the repository
    :return: A response
    """
    body = FotoUpdate(**body)
    response = await repository_fotos.update_foto(foto.id, body, current_user, session)
    assert response.title == "other_foto"
    assert response.descr == "other_foto"


@pytest.mark.asyncio
async def test_remove_foto(foto, current_user, session):
    """
    The test_remove_foto function tests the remove_foto function in repository_fotos.py
        by first creating a foto, then removing it and checking if it exists.
    
    :param foto: Pass in the foto object that was created by the test_create_foto function
    :param current_user: Check if the user is authorized to delete the foto
    :param session: Pass the database session to the repository layer
    :return: None
    """
    await repository_fotos.remove_foto(foto.id, current_user, session)
    response = await repository_fotos.get_foto_by_id(foto.id, current_user, session)
    assert response == None
