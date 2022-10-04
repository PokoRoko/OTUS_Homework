import pytest
from oop_api_03.api import OnlineScoreRequest


@pytest.fixture(scope="function")
def score_request():
    return OnlineScoreRequest(request_body={"test_body": "test"})


def test_length_less_than_eleven_int_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.phone = 72


def test_length_less_than_eleven_str_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.phone = "72"


def test_list_integers_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.phone = [1, 2, 3]


def test_set_integers_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.phone = {1, 2, 3}


def test_empty_dict_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.phone = dict()


def test_byte_string_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.phone = b"byte_name"


def test_not_starts_with_seven_int_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.phone = 89267775190


def test_not_starts_with_seven_str_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.phone = "89267775190"


def test_valid_phone_number_str(score_request):
    test_valid_phone_num_str = "79267775190"
    score_request.phone = test_valid_phone_num_str
    assert score_request.phone == test_valid_phone_num_str


def test_valid_phone_number_int(score_request):
    test_valid_phone_num_int = 79267775190
    score_request.phone = test_valid_phone_num_int
    assert score_request.phone == test_valid_phone_num_int
