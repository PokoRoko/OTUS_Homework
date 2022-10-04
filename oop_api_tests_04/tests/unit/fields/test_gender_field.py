import pytest
from oop_api_03.api import OnlineScoreRequest


@pytest.fixture()
def score_request():
    return OnlineScoreRequest(request_body={"test_body": "test"})


def test_integer_except_zero_one_two_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.gender = 3


def test_list_integers_is_not_valid(score_request):
    with pytest.raises(TypeError):
        score_request.gender = [1, 2, 3]


def test_set_integers_is_not_valid(score_request):
    with pytest.raises(TypeError):
        score_request.gender = {1, 2, 3}


def test_empty_dict_is_not_valid(score_request):
    with pytest.raises(TypeError):
        score_request.gender = dict()


def test_byte_string_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.gender = b"byte_name"


def test_zero_one_or_two_are_valid_values(score_request):
    for valid_value in (0, 1, 1):
        score_request.gender = valid_value
        assert score_request.gender == valid_value
