import pytest

from oop_api_03.api import ClientsInterestsRequest


@pytest.fixture(scope="function")
def clients_interests_request():
    return ClientsInterestsRequest(request_body={"test_body": "test"})


def test_integer_is_not_valid(clients_interests_request):
    with pytest.raises(ValueError):
        clients_interests_request.client_ids = 42


def test_set_integers_is_not_valid(clients_interests_request):
    with pytest.raises(ValueError):
        clients_interests_request.client_ids = {1, 2, 3}


def test_empty_dict_is_not_valid(clients_interests_request):
    with pytest.raises(ValueError):
        clients_interests_request.client_ids = dict()


def test_byte_string_is_not_valid(clients_interests_request):
    with pytest.raises(ValueError):
        clients_interests_request.client_ids = b"some_name"


def test_list_with_at_least_one_string_is_not_valid(clients_interests_request):
    with pytest.raises(ValueError):
        clients_interests_request.client_ids = [1, 2, "3"]


def test_tuple_with_at_least_one_string_is_not_valid(clients_interests_request):
    with pytest.raises(ValueError):
        clients_interests_request.client_ids = (1, 2, "3")


def test_list_integers_is_valid(clients_interests_request):
    test_valid_client_ids_value = [1, 2, 3]
    clients_interests_request.client_ids = test_valid_client_ids_value
    assert clients_interests_request.client_ids == test_valid_client_ids_value


def test_tuple_integers_is_valid(clients_interests_request):
    test_valid_client_ids_value = (1, 2, 3)
    clients_interests_request.client_ids = test_valid_client_ids_value
    assert clients_interests_request.client_ids == test_valid_client_ids_value
