from datetime import datetime

import io
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

from src.database.models import User, Foto
from src.services.auth import auth_service
from src.conf.messages import NOT_FOUND


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.foto("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_verify = True
    session.commit()
    response = client.foto(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture()
def foto(user, token, session):
    """
    The foto function is used to create a foto for the user.
        It takes in the user, token and session as parameters.
        The function first checks if there is already a foto created for that particular user. If not, it creates one with all the necessary details and adds it to the database.
    
    :param user: Get the user_id of the current user
    :param token: Authenticate the user
    :param session: Access the database
    :return: A foto object
    """
    cur_user = session.query(User).filter(User.email == user['email']).first()
    foto = session.query(Foto).first()
    if foto is None:
        foto = Foto(
            image_url="https://res.cloudinary.com/dybgf2pue/image/upload/c_fill,h_250,w_250/Dominic",
            title="cat",
            descr="pet",
            tags=["cat", "pet"],
            created_at=datetime.now(),
            user_id=cur_user.id,
            public_id="Dominic",
            done=True
        )
        session.add(foto)
        session.commit()
        session.refresh(foto)
    return foto


@pytest.fixture()
def new_user(user, token, session):
    """
    The new_user function takes in a user, token, and session.
    It then queries the database for a user with the same email as the one passed in.
    If there is no such user, it creates one using information from the passed-in 
    user object and adds it to our database. It then returns this new_user.
    
    :param user: Create a new user object
    :param token: Create a new token for the user
    :param session: Query the database for a user with the same email as the one provided in the request
    :return: A new user object
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


def test_create_foto(client, token):
    """
    The test_create_foto function tests the FOTO /api/fotos/new endpoint.
    It does so by creating a new foto with a title, description, and tags.
    The test also checks that the response status code is 201 (created) and that 
    the returned data contains all of the information we sent in our request.
    
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A response with a 201 status code and the data from the foto
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None 
        file_data = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
        image.save(file_data, 'jpeg')
        file_data.seek(0)
        data = {
            "title": "test_foto",
            "descr": "test_foto",
            "tags": ["test_foto"]
            }
        
        response = client.post(
            "/api/fotos/new/",
            headers={"Authorization": f"Bearer {token}"},
            data=data,
            files={"file": ("test.jpg", file_data, "image/jpeg")}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["title"] == "test_foto"
        assert data["descr"] == "test_foto"
        assert data["image_url"] != None
        assert "id" in data


def test_get_all_fotos(client, token):
    """
    The test_get_all_fotos function tests the /api/fotos/all endpoint.
    It does this by first patching the redis_cache function in auth_service to return None, which will cause a call to be made
    to get all fotos from the database. It then makes a GET request to /api/fotos/all with an Authorization header containing
    a valid JWT token and checks that it returns 200 OK and that data is returned as expected.
    
    :param client: Make the request to the api
    :param token: Make sure that the user is authorized to access the endpoint
    :return: A list of all fotos
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/all/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["title"] == "test_foto"
        assert "id" in data[0]


def test_get_get_my_fotos(client, token):
    """
    The test_get_get_my_fotos function tests the get_my_fotos endpoint.
    It does this by first patching the redis cache to return None, which will cause a call to be made to the database.
    Then it makes a GET request with an Authorization header containing a valid token and checks that:
        - The response status code is 200 OK, and if not prints out the response text for debugging purposes.
        - The data returned is in JSON format (a list).  If not, print out error message for debugging purposes.
        - That there are two items in data[0] (the first item of data), one being
    
    :param client: Make requests to the server
    :param token: Authenticate the user
    :return: All fotos created by the user who is logged in
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/my_fotos/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["title"] == "test_foto"
        assert "id" in data[0]


def test_get_foto_by_id(foto, client, token):
    """
    The test_get_foto_by_id function tests the get_foto_by_id endpoint.
    It does this by first creating a foto, then using the client to make a GET request to /api/fotos/by_id/&lt;foto.id&gt;.
    The response is checked for status code 200 and that it contains the correct data.
    
    :param foto: Create a foto for the test
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A foto by id
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/by_id/{foto.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "test_foto"
        assert "id" in data


def test_get_foto_by_id_not_found(foto, client, token):
    """
    The test_get_foto_by_id_not_found function tests the get_foto_by_id function in the fotos.py file.
    It does this by creating a foto, then using that foto's id to create a client and token for testing purposes.
    Then it uses patch to mock out redis cache, which is used in auth service (which is imported at the top of this file).
    The mocked redis cache returns None when called upon, which means that there will be no user found with that id. 
    This should result in an error 404 response code being returned from our server.
    
    :param foto: Create a foto in the database
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A 404 status code and a detail message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/by_id/{foto.id+1}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_fotos_by_user_id(new_user, client, token):
    """
    The test_get_fotos_by_user_id function tests the get_fotos_by_user_id function in fotos.py.
    It does this by creating a new user, and then using that user's id to create a foto with the title &quot;test&quot; and description &quot;test&quot;.
    Then it uses client to make a GET request for all of the fotos created by that user, which should be just one foto. 
    The response is checked for status code 200 (OK), and then data is extracted from it as json format.
    
    :param new_user: Create a new user in the database
    :param client: Make a request to the server
    :param token: Test the authorization of a user
    :return: A list of fotos that belong to the user
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/by_user_id/{new_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["title"] == "test_foto"
        assert data[0]["descr"] == "test_foto"
        

def test_get_fotos_by_user_id_not_found(new_user, client, token):
    """
    The test_get_fotos_by_user_id_not_found function tests the get_fotos_by_user_id function in the fotos.py file.
    It does this by creating a new user, then using that user's id to create a foto and add it to the database.
    Then, it uses client to make a GET request for all of that user's fotos (which should be just one). It asserts 
    that response is successful and has status code 200.
    
    :param new_user: Create a new user
    :param client: Make requests to the api
    :param token: Pass the token to the function
    :return: 404
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/by_user_id/{new_user.id+1}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_foto_by_title(foto, client, token):
    """
    The test_get_foto_by_title function tests the get_foto_by_title function in fotos.py.
    It does this by creating a foto, then using the client to make a GET request to /api/fotos/by_title/{foto.title}.
    The response is checked for status code 200 and data[0][&quot;image&quot;] is checked for not being None.
    
    :param foto: Pass in a foto object to the test function
    :param client: Send a request to the server
    :param token: Authenticate the user
    :return: The data of the foto with the title that was passed as a parameter
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/by_title/{foto.title}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["title"] == "test_foto"
        assert data[0]["descr"] == "test_foto"
        assert data[0]["image_url"] != None


def test_get_foto_by_title_not_found(client, token):
    """
    The test_get_foto_by_title_not_found function tests the get_foto_by_title function in fotos.py
        It does this by mocking the redis cache and returning None, which will cause a 404 error to be returned
        The test then checks that the status code is 404 and that data[&quot;detail&quot;] == NOT_FOUND
    
    :param client: Make a request to the api
    :param token: Authenticate the user
    :return: A 404 error
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/fotos/by_title/other_test",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_fotos_by_username(new_user, client, token):
    """
    The test_get_fotos_by_username function tests the get_fotos_by_username function in the fotos.py file.
    The test uses a new user and client to create a foto, then it gets that foto by username using the 
    get_fotos_by_username function and checks if it is equal to what was created.
    
    :param new_user: Create a new user in the database
    :param client: Make requests to the app
    :param token: Pass in the token to the test function
    :return: A list of fotos by a username
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/by_username/{new_user.username}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["title"] == "test_foto"
        assert data[0]["descr"] == "test_foto"
        

def test_get_fotos_by_username_not_found(client, token):
    """
    The test_get_fotos_by_username_not_found function tests the get_fotos_by_username function in fotos.py
    to ensure that it returns a 404 status code and NOT FOUND detail when the username is not found.
    
    :param client: Make requests to the api
    :param token: Pass the token to the test function
    :return: 404 status code and not_found message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/by_username/test_user_name",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND
        

def test_get_fotos_with_tag_not_found(client, token):
    """
    The test_get_fotos_with_tag_not_found function tests the get_fotos_with_tag function in fotos.py
        It does this by mocking the redis cache and returning None, which will cause a 404 error to be returned.
        The test then checks that the status code is indeed 404, and that data[&quot;detail&quot;] == NOT_FOUND.
    
    :param client: Make a request to the api
    :param token: Pass the token to the test function
    :return: 404 if the tag does not exist
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/with_tag/test_new_tag",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_read_foto_comments_not_found(foto, client, token):
    """
    The test_read_foto_comments_not_found function tests the read_foto_comments function in the fotos.py file.
    The test is testing to see if a foto that does not exist will return a 404 error.
    
    :param foto: Create a foto object that is used to test the function
    :param client: Make a request to the api
    :param token: Test the read_foto_comments function with a valid token
    :return: A 404 status code and a not_found message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/comments/all/{foto.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_read_foto_by_keyword_not_found(client, token):
    """
    The test_read_foto_by_keyword_not_found function tests the read_foto_by_keyword function in the fotos.py file.
    The test is testing that if a keyword is not found, then it will return a 404 error and NOT FOUND message.
    
    :param client: Make requests to the api
    :param token: Pass the token to the function
    :return: A 404 status code and a not_found message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/fotos/by_keyword/test_keyword",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_fotos(client, token):
    """
    The test_get_fotos function tests the /api/fotos/all endpoint.
    It does this by first patching the auth_service module's redis_cache object, and then setting its get method to return None.
    Then it makes a GET request to /api/fotos/all with an Authorization header containing a valid token.
    The response should have status code 200, and its data should be a list of at least one foto.
    
    :param client: Make a request to the api
    :param token: Authenticate the user
    :return: A list of fotos
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/fotos/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


def test_update_foto(foto, client, token):
    """
    The test_update_foto function tests the update_foto function in app.py.
    It does this by creating a foto, then using the client to send a PUT request to /api/fotos/&lt;id&gt; with json data containing title, descr and tags fields.
    The response is checked for status code 200 (OK) and that it contains the correct data.
    
    :param foto: Pass the foto object to the test function
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: 200
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/fotos/{foto.id}",
            json={
                "title": "other_foto",
                "descr": "other_foto",
                "tags": ["other_foto"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "other_foto"
        assert data["descr"] == "other_foto"
        assert "id" in data


def test_update_foto_not_found(foto, client, token):
    """
    The test_update_foto_not_found function tests the update_foto function in the fotos.py file.
    It does this by creating a foto, then using client to send a PUT request to /api/fotos/{foto.id+2} with json data and an authorization header containing token as its value, which is created from user's id and password hash (see test_create_user).
    The response status code should be 404 because there is no foto with id {foto.id+2}. The response text should contain NOT FOUND.
    
    :param foto: Create a foto in the database
    :param client: Make requests to the api
    :param token: Test the update foto endpoint with a valid token
    :return: A 404 error code and the detail is not_found
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/fotos/{foto.id+1}",
            json={
                "title": "other_foto",
                "descr": "other_foto",
                "tags": ["other_foto"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_delete_foto(foto, client, token):
    """
    The test_delete_foto function tests the delete_foto function in the fotos.py file.
    It does this by creating a foto, then deleting it using the client and token created in conftest.py
    The patch object is used to mock out redis_cache so that we can test without having to use Redis
    
    :param foto: Pass the foto fixture into the function
    :param client: Make a request to the api
    :param token: Authenticate the user
    :return: The data of the deleted foto
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/fotos/{foto.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "other_foto"
        assert data["descr"] == "other_foto"
        assert "id" in data


def test_repeat_delete_foto(client, token):
    """
    The test_repeat_delete_foto function tests the repeat deletion of a foto.
        The test_repeat_delete_foto function takes in client and token as parameters.
        The test_repeat_delete_foto function uses patch to mock the redis cache object from auth service.
        The test returns None for redis cache get method, which is used to check if a user is logged in or not. 
        If there is no user logged in, then it will return None and raise an error that says &quot;User not found&quot;. 
    
    :param client: Make requests to the api
    :param token: Pass in the token to be used for testing
    :return: 404 error and not_found message
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/fotos/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND
