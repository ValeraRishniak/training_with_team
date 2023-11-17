from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User, Foto
from src.services.auth import auth_service
from src.conf.messages import NOT_FOUND


@pytest.fixture()
def token(client, user, session, monkeypatch):
    """
    The token function is used to create a user, verify the user, and then log in as that user.
    It returns an access token for use in other tests.
    
    :param client: Make requests to the api
    :param user: Create a user in the database
    :param session: Access the database
    :param monkeypatch: Mock the send_email function
    :return: A token, which is used to test the protected endpoints
    """
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_verify = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture()
def foto_id(user, token, session):
    """
    The foto_id function takes in a user, token, and session.
    It then queries the database for the first foto. If there is no foto it creates one with default values.
    The function returns the id of that foto.
    
    :param user: Get the user from the database
    :param token: Check if the user is logged in
    :param session: Query the database
    :return: The id of the foto
    """
    cur_user = session.query(User).filter(User.email == user['email']).first()
    foto = session.query(Foto).first()
    if foto is None:
        foto = Foto(
            image_url="https://res.cloudinary.com/dybgf2pue/image/upload/c_fill,h_250,w_250/Dominic",
            title="cat",
            descr="pet",
            created_at=datetime.now(),
            user_id=cur_user.id,
            public_id="Dominic",
            done=True
        )
        session.add(foto)
        session.commit()
        session.refresh(foto)
    return foto.id


@pytest.fixture()
def body():
    return {
        "circle": {
            "use_filter": True,
            "height": 400,
            "width": 400
        },
        "effect": {
            "use_filter": False,
            "art_audrey": False,
            "art_zorro": False,
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
            "use_filter": False,
            "font_size": 70,
            "text": ""
        },
        "rotate": {
            "use_filter": True,
            "width": 400,
            "degree": 45
        }
    }



def test_transform_metod(client, foto_id, body, token):
    """
    The test_transform_metod function tests the transform_metod function in the transformations.py file.
    It does this by patching the redis_cache object from auth_service and setting its get method to return None,
    then it sends a PATCH request to /api/transformations/{foto_id} with a json body containing an image url and 
    a token as headers, then it asserts that response status code is 200 (OK) and that data['transform_url'] is not None.
    
    :param client: Create a test client for the flask app
    :param foto_id: Get the foto id from the url
    :param body: Pass the json data to the endpoint
    :param token: Get the token from the fixture
    :return: None
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(f'/api/transformations/{foto_id}', json=body,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data.get('transform_url') is not None


def test_transform_metod_not_found(client, foto_id, body, token):
    """
    The test_transform_metod_not_found function tests the following:
        1. The response status code is 404 (Not Found)
        2. The response body contains a detail key with value NOT_FOUND
    
    :param client: Make requests to the api
    :param foto_id: Create a foto_id+2
    :param body: Pass the body of the request to be sent
    :param token: Pass the token to the test function
    :return: 404, but the correct answer is 200
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(f'/api/transformations/{foto_id+1}', json=body,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_show_qr(client, foto_id, user, token):
    """
    The test_show_qr function tests the show_qr function in transformations.py
    by mocking the redis cache and checking that a 200 response is returned with 
    a string as data.
    
    :param client: Make a request to the api
    :param foto_id: Pass the foto_id to the test function
    :param user: Pass the user data to the function
    :param token: Authenticate the user
    :return: A string
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.foto(f'/api/transformations/qr/{foto_id}', json=user,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, str)


def test_show_qr_not_found(client, foto_id, user, token):
    """
    The test_show_qr_not_found function tests the show_qr function in transformations.py
        to ensure that it returns a 404 status code and an appropriate error message when 
        the foto ID is not found in Redis.
    
    :param client: Make a request to the api
    :param foto_id: Generate a random id for the foto that is created in the database
    :param user: Create a user object that is passed in the request body
    :param token: Pass the token to the function
    :return: A 404 error
    """
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.post(f'/api/transformations/qr/{foto_id+1}', json=user,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND
    