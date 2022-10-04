import pytest

from oop_api_03.api import MethodRequest


@pytest.fixture(scope="function")
def method_request():
    return MethodRequest(request_body={"test_body": "test"})


def test_integer_is_not_valid(method_request):
    with pytest.raises(ValueError):
        method_request.arguments = 42


def test_list_integers_is_not_valid(method_request):
    with pytest.raises(ValueError):
        method_request.arguments = [1, 2, 3]


def test_set_integers_is_not_valid(method_request):
    with pytest.raises(ValueError):
        method_request.arguments = {1, 2, 3}


def test_empty_dict_is_valid(method_request):
    method_request.arguments = dict()
    assert method_request.arguments == dict()


def test_byte_string_is_not_valid(method_request):
    with pytest.raises(ValueError):
        method_request.arguments = b"byte string"


def test_none_is_not_valid(method_request):
    with pytest.raises(ValueError):
        method_request.arguments = None
