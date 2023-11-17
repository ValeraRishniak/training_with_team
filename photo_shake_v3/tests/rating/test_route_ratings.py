import json
from unittest.mock import MagicMock
from datetime import datetime
import pytest

from src.database.models import User, Foto

from src.services.auth import auth_service


@pytest.mark.parametrize("foto_id, user_id, result", [
    (1, 1, 200),  # own foto
    (2, 2, 200)  # another user
])
def test_create_foto(session, foto_id, user_id, result):
    """
    The test_create_foto function creates a new foto object and adds it to the database.
        Args:
            session (sqlalchemy.orm.sessionmaker): The SQLAlchemy session used for interacting with the database.
            foto_id (int): The ID of the foto being created in this function call, which is also its primary key in 
                the database table that stores fotos' information.
            user_id (int): The ID of the user who created this foto, which is also its foreign key in 
                the database table that stores fotos' information.
    
    :param session: Create a foto in the database
    :param foto_id: Set the id of the foto
    :param user_id: Create a user_id for the foto
    :param result: Store the result of the test
    :return: The foto object
    """
    test_foto = Foto()
    test_foto.id = foto_id
    test_foto.image_url = "image_url"
    test_foto.transform_url = "transform_url"
    test_foto.title = "title"
    test_foto.descr = "descr"
    test_foto.created_at = datetime.now()
    test_foto.updated_at = datetime.now()
    test_foto.done = True
    test_foto.user_id = user_id
    test_foto.tags = []
    test_foto.public_id = "888"
    test_foto.avg_rating = None

    session.add(test_foto)
    session.commit()


@pytest.fixture()
def token(client, user, session, monkeypatch):
    """
    The token function is used to create a user, verify the user, and then log in as that user.
    It returns an access token for use in other tests.
    
    :param client: Send requests to the api
    :param user: Create a user in the database
    :param session: Create a new session in the database
    :param monkeypatch: Mock the send_email function
    :return: A token, which is used to access the protected endpoint
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


@pytest.mark.parametrize("foto_id, rate, result", [
    (1, 5, 423),  # Response [423 Locked]
    (2, 3, 200),  # Response [200]
    (3, 3, 404)  # Response [404]
])
def test_create_rating(session, client, token, foto_id, rate, result):
    """
    The test_create_rating function tests the create_rating function in the ratings.py file.
    It does this by sending a POST request to the api/ratings/fotos/{foto_id} endpoint with a rate of 1 or - 1, and an Authorization header containing a valid token for an existing user account.
    The test passes if it receives back either 201 Created or 400 Bad Request.
    
    :param session: Create a database session
    :param client: Make requests to the api
    :param token: Authenticate the user
    :param foto_id: Specify the foto that is being rated
    :param rate: Set the rating value for a foto
    :param result: Check the status code of the response
    :return: A 200 status code, which means that the test was successful
    """
    response = client.post(
        f"api/ratings/fotos/{foto_id}/{rate}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


@pytest.mark.parametrize("rate_id, new_rate, result", [
    (1, 5, 200),
    (2, 3, 404),
    (3, 3, 404)
])
def test_edit_rating(session, client, token, rate_id, new_rate, result):
    """
    The test_edit_rating function tests the edit_rating endpoint.
        It takes in a session, client, token, rate_id (the id of the rating to be edited), new_rate (the new rating value), and result (expected status code).
        The function then makes a PUT request to the edit_rating endpoint with an Authorization header containing the token.
        Finally it asserts that response's status code is equal to result.
    
    :param session: Create a database session
    :param client: Make requests to the api
    :param token: Authenticate the user
    :param rate_id: Identify the rating to be edited
    :param new_rate: Set the new rating value
    :param result: Determine the expected status code of the response
    :return: A 200 status code, which means that the test was successful
    """
    response = client.put(
        f"api/ratings/edit/{rate_id}/{new_rate}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


@pytest.mark.parametrize("rate_id, result", [
    (1, 200),
    (2, 404),
    (3, 404)
])
def test_delete_rating(session, client, token, rate_id, result):
    """
    The test_delete_rating function tests the DELETE /api/ratings/delete/{rate_id} endpoint.
    It takes in a session, client, token, rate_id and result as arguments.
    The function then makes a request to the endpoint with the given rate_id and checks if it returns 
    the expected status code.
    
    :param session: Create a database session
    :param client: Make requests to the api
    :param token: Authenticate the user
    :param rate_id: Pass the id of the rating to be deleted
    :param result: Check the status code of the response
    :return: A 200 status code
    """
    response = client.delete(
        f"api/ratings/delete/{rate_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


@pytest.mark.parametrize("foto_id, rate, result", [
    (1, 5, 423),  # Response [423 Locked]
    (2, 3, 200),  # Response [200]
    (3, 3, 404)  # Response [404]
])
def test_create_rating_2(session, client, token, foto_id, rate, result):
    """
    The test_create_rating_2 function tests the POST /api/ratings/fotos/{foto_id} endpoint.
    It takes in a session, client, token, foto_id and rate as parameters. The test will fail if the response status code is not equal to 200.
    
    :param session: Create a new database session for the test
    :param client: Make requests to the api
    :param token: Authenticate the user
    :param foto_id: Pass the foto id to the test function
    :param rate: Determine the rating of the foto
    :param result: Check if the response code is correct
    :return: A 200 status code
    """
    response = client.post(
        f"api/ratings/fotos/{foto_id}/{rate}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


def test_all_ratings(session, client, token):
    """
    The test_all_ratings function tests the GET /api/ratings/all endpoint.
    It does so by making a request to the endpoint, and then asserting that:
        1) The response status code is 200 (OK).
        2) The response data is of type list.

    :param session: Create a database session
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A list of all the ratings in the database
    """

    response = client.get(
        "api/ratings/all",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert type(response.json()) == list


def test_all_my_rates(session, client, token):
    """
    The test_all_my_rates function tests the all_my endpoint.
    It does so by first creating a user, then logging in to get a token.
    Then it creates two ratings for that user and one rating for another user.
    Finally, it makes an API call to the all_my endpoint with the token of our test user and checks that only two ratings are returned.
    
    :param session: Create a database session
    :param client: Make requests to the api
    :param token: Authenticate the user
    :return: A list of all the ratings that the user has made
    """
    response = client.get(
        "api/ratings/all_my",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert type(response.json()) == list


@pytest.mark.parametrize("user_id, foto_id, result", [
    (1, 2, 200),
    (1, 3, 404)
])
def test_user_for_foto(session, client, token, user_id, foto_id, result):
    """
    The test_user_for_foto function tests the user_for_foto endpoint.
        Args:
            session (object): The database session object.
            client (object): The Flask test client object.
            token (str): A valid JWT token string for a registered user account. 
                This is used to authenticate requests made to the API endpoints being tested in this function,
                and must be passed as an argument when calling this function from another module or script file, e.g.:

    :param session: Create a database session for the test
    :param client: Make a request to the api
    :param token: Authenticate the user
    :param user_id: Get the user_id from the database
    :param foto_id: Get the foto_id from the test data
    :param result: Check the status code of the response
    :return: A 200 status code
    """
    response = client.get(
        f"api/ratings/user_foto/{user_id}/{foto_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result

