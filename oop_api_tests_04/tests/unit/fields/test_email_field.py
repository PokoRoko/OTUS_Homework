import pytest
from oop_api_03.api import OnlineScoreRequest


@pytest.fixture()
def score_request():
    return OnlineScoreRequest(request_body={"test_body": "test"})


def test_integer_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.email = 42


def test_list_integers_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.email = [1, 2, 3]


def test_set_integers_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.email = {1, 2, 3}


def test_empty_dict_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.email = dict()


def test_byte_string_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.email = b"byte_email"


def test_string_without_at_sign_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.email = "email"


def test_string_with_at_sign_is_valid(score_request):
    valid_test_value = "name@host.ru"
    score_request.email = valid_test_value
    assert score_request.email == valid_test_value
