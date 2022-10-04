import datetime

import pytest
from dateutil.relativedelta import relativedelta

from oop_api_03.api import OnlineScoreRequest


@pytest.fixture()
def score_request():
    return OnlineScoreRequest(request_body={"test_body": "test"})


def test_integer_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.birthday = 42


def test_list_integers_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.birthday = [1, 2, 3]


def test_byte_string_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.birthday = b"some_name"


def test_year_month_day_format_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.birthday = "2022.02.23"


def test_month_day_year_format_is_not_valid(score_request):
    with pytest.raises(ValueError):
        score_request.birthday = "02.23.2022"


def test_birthday_from_future_is_not_valid(score_request):
    current_date = datetime.datetime.today()
    tomorrow_date = current_date + relativedelta(days=1)
    tomorrow_date_as_string = tomorrow_date.strftime("%d.%m.%Y")
    with pytest.raises(ValueError):
        score_request.birthday = tomorrow_date_as_string


def test_birthday_more_70_years_ago_is_not_valid(score_request):
    current_date = datetime.datetime.today()
    more_than_seventy_years_ago_date = current_date + relativedelta(years=-70, days=-1)
    more_than_seventy_years_ago_date_as_string = more_than_seventy_years_ago_date.strftime("%d.%m.%Y")
    with pytest.raises(ValueError):
        score_request.birthday = more_than_seventy_years_ago_date_as_string


def test_birthday_exactly_70_years_ago_is_valid(score_request):
    current_date = datetime.datetime.today()
    exactly_seventy_years_ago_date = current_date + relativedelta(years=-69)
    exactly_seventy_years_ago_date_as_string = exactly_seventy_years_ago_date.strftime("%d.%m.%Y")
    score_request.birthday = exactly_seventy_years_ago_date_as_string
    assert score_request.birthday == exactly_seventy_years_ago_date_as_string


def test_day_month_year_format_is_valid(score_request):
    test_valid_birthday_value = "23.02.2022"
    score_request.birthday = test_valid_birthday_value
    assert score_request.birthday == test_valid_birthday_value
