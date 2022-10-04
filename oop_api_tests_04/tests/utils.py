import datetime
import hashlib
import json
from typing import Dict, List, Optional, Union

from oop_api_03 import api


class KeyValueTestStorage:
    def __init__(self):
        self._kv_store = dict()

    def get(self, key: str) -> str:
        return self._kv_store[key]

    def set(self, key: str, value: List[str]):
        self._kv_store[key] = json.dumps(value)

    def cache_get(self, key: str) -> Optional[Union[int, float]]:
        return self._kv_store.get(key)

    def cache_set(self, key: str, value: Union[int, float], expire_time: int) -> None:
        self._kv_store[key] = value

    def clear(self) -> None:
        self._kv_store.clear()

def set_valid_auth(request: Dict[str, Union[str, Dict, int]]):
    if request.get("login") == api.ADMIN_LOGIN:
        request["token"] = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).encode()).hexdigest()
    else:
        msg = request.get("account", "") + request.get("login", "") + api.SALT
        request["token"] = hashlib.sha512(msg.encode("utf-8")).hexdigest()