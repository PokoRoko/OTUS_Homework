import datetime
import hashlib
import json
from typing import List, Optional, Union

from oop_api_tests_04.store import KeyValueStorage


def get_score(store: KeyValueStorage,
              phone: Optional[Union[str, int]],
              email: Optional[str],
              birthday: Optional[datetime.date] = None,
              gender: Optional[int] = None,
              first_name: Optional[str] = None,
              last_name: Optional[str] = None) -> Union[int, float]:

    key_parts = [first_name or "",
                 last_name or "",
                 str(phone) or "",
                 birthday if birthday is not None else "", ]

    key = "uid:" + hashlib.md5("".join(key_parts).encode()).hexdigest()
    score = store.cache_get(key) or 0

    if score:
        return score
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache expire 60 minutes
    store.cache_set(key, score, expire_time=60 * 60)

    return score


def get_interests(store: KeyValueStorage, cid: int) -> List[str]:
    r = store.get(f"i:{cid}")
    return json.loads(r) if r else []
