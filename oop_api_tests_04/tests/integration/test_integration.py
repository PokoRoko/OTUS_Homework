import random

import pytest
from redis.exceptions import ConnectionError

from oop_api_tests_04.store import KeyValueStorage

TEST_RETRIES = 3
TEST_TIMEOUT = 3


@pytest.fixture()
def working_store(request):
    def clear_store():
        store.clear()

    store = KeyValueStorage(host="localhost", port=6379, retries=TEST_RETRIES, timeout=TEST_TIMEOUT)
    request.addfinalizer(clear_store)
    return store


@pytest.fixture()
def not_working_store():
    not_working_store = KeyValueStorage(host="wrong_host", port=404, retries=TEST_RETRIES, timeout=TEST_TIMEOUT)
    return not_working_store


def test_get_key_from_cache(working_store):
    test_value = random.randint(1, 200)
    test_key = "test_key"
    working_store.cache_set(test_key, test_value, expire_time=60 * 60)
    assert working_store.cache_get(test_key) == test_value


def test_get_non_wrong_key_from_cache(working_store):
    assert working_store.cache_get("wrong_key") is None


def test_get_non_wrong_key_from_storage(working_store):
    assert working_store.get("wrong_key") is None


def test_get_key_from_closed_cache(not_working_store):
    test_key = "test_key_for_not_working_cache"
    not_working_store.cache_set(test_key, 404, expire_time=60 * 60)

    assert not_working_store.cache_get(test_key) is None
    assert not_working_store.get.calls == not_working_store.retries


def test_get_key_from_closed_storage(not_working_store):
    with pytest.raises(ConnectionError):
        assert not_working_store.get("non_existent_key")
