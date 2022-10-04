import logging
from functools import wraps
from typing import Callable, NoReturn, Optional, Union

from redis.client import Redis
from redis.exceptions import ConnectionError, TimeoutError


def make_retries(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *method_args, **method_kwargs):
        result = None
        try:
            result = method(self, *method_args, **method_kwargs)
        except (ConnectionError, TimeoutError) as exception:
            logging.error("`Unknown error. Retrying.")
            if wrapper.calls >= self.retries:
                raise exception
            wrapper.calls += 1
            self._reset_connection()
            wrapper(self, *method_args, **method_kwargs)
        return result

    wrapper.calls = 0
    return wrapper


class KeyValueStorage:
    def __init__(self, host: str, port: int, retries: int, timeout: int):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self._kv_storage = None
        self._connect()

    def _connect(self) -> NoReturn:
        try:
            self._kv_storage = Redis(host=self.host, port=self.port, socket_timeout=self.timeout)
            self._kv_storage.ping()
        except Exception as error:
            logging.error(f"Error redis {self.host}:{self.port} connecting. Error: {error}")

    def _reset_connection(self) -> NoReturn:
        self._kv_storage.close()
        self._connect()

    @make_retries
    def get(self, key: str) -> str:
        result = self._kv_storage.get(key)
        return result.decode() if result is not None else result

    def cache_get(self, key: str) -> Optional[float]:
        result = None
        try:
            result = self.get(key)
        except (ConnectionError, TimeoutError) as error:
            logging.error(f"Error get value from cache. Error: {error}")

        return float(result) if result is not None else result

    @make_retries
    def _set(self, key: str, value: Union[float, int], key_expire_time_sec: int) -> None:
        self._kv_storage.set(key, str(value), ex=key_expire_time_sec)

    def cache_set(self, key: str, value: Union[float, int], expire_time: int) -> None:
        try:
            self._set(key, str(value), key_expire_time_sec=expire_time)
        except (ConnectionError, TimeoutError) as error:
            logging.error(f"Error set value to cache. Error: {error}")

    def clear(self) -> NoReturn:
        self._kv_storage.flushall()
