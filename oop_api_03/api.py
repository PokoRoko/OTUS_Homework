#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import json
import logging
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser
from typing import Any, Dict, List, Optional, Tuple, Union

from dateutil.relativedelta import relativedelta

if __name__ == "oop_api_03.api":
    from oop_api_tests_04.scoring import get_interests, get_score
else:
    from scoring import get_interests, get_score

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"

UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

PHONE_LENGTH = 11
CODE_CITY_PHONE = 7

MAX_AGE = 70


class BaseField:
    def __init__(self, required: bool, nullable: bool) -> None:
        self.required = required
        self.nullable = nullable

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set_name__(self, owner, name: str):
        self.name = name

    def _check_field(self, value: Any) -> None:
        if value is None and self.required:
            raise ValueError(f"Field {self.name} is required")

        if not self.nullable and value in ("", (), [], {}):
            raise ValueError(f"Field {self.name} is not nullable but empty value found")

    def _validate(self, value: Any) -> None:
        self._check_field(value)

    def __set__(self, instance: Any, value: Any) -> None:
        self._validate(value)
        instance.__dict__[self.name] = value


class CharField(BaseField):
    def _validate(self, value: str) -> None:
        super()._validate(value)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{self.__class__.__name__} invalid value type: {type(value)}")

    def __add__(self, other):
        result = CharField(required=self.required, nullable=self.nullable)
        result_value = f"{self.__dict__[self.name]} {other.__dict__[self.name]}"
        result.__dict__[self.name] = result_value


class ArgumentsField(BaseField):
    def _validate(self, value: Dict[str, Union[int, str]]) -> None:
        super()._validate(value)
        try:
            if not isinstance(value, dict):
                raise ValueError(f"{self.__class__.__name__} invalid value type, can be dict")
            json.dumps(value)
        except TypeError:
            raise ValueError(f"{self.__class__.__name__} invalid json format")


class EmailField(CharField):
    def _validate(self, value: str) -> None:
        super()._validate(value)
        if value and "@" not in value:
            raise ValueError(f"Email must include '@': {value}")


class PhoneField(BaseField):
    def _validate(self, value: Union[int, str]) -> None:
        super()._validate(value)
        if value is not None:
            if not isinstance(value, (int, str)):
                raise ValueError(f"Phone number must be int or str, not {type(value)}")

            if len(str(value)) != PHONE_LENGTH:
                raise ValueError(f"Invalid number length len{(str(value))}. "
                                 f"Expected length {PHONE_LENGTH}")

            if not str(value).startswith(str(CODE_CITY_PHONE)):
                raise ValueError(f"Invalid code city number {value}. "
                                 f"Expected code {CODE_CITY_PHONE}")


class DateField(BaseField):
    def _validate(self, value: str) -> None:
        super()._validate(value)
        if value is not None:
            datetime.datetime.strptime(value, "%d.%m.%Y")


class BirthDayField(BaseField):
    def _validate(self, value: str) -> None:
        super()._validate(value)
        if value:
            if not isinstance(value, str):
                raise ValueError(f"Invalid type to date. Date cannot be {type(value)} or empty")
            elif datetime.datetime.strptime(value, "%d.%m.%Y") < datetime.datetime.now() - relativedelta(years=MAX_AGE):
                raise ValueError(f"Invalid date of birth. Date cannot be more than {MAX_AGE} years")
            elif datetime.datetime.strptime(value, "%d.%m.%Y") > datetime.datetime.now():
                raise ValueError(f"Invalid date of birth. Date cannot be in future {type(value)}")


class GenderField(BaseField):
    def _validate(self, value: int) -> None:
        super()._validate(value)
        if value is not None and value not in GENDERS:
            raise ValueError(f"Value can be is one {GENDERS}")


class ClientIDsField(BaseField):
    def __init__(self, required: bool, nullable: bool = False) -> None:
        super().__init__(required, nullable)

    def _validate(self, value: Optional[List[int]]) -> None:
        super()._validate(value)
        if not value or not isinstance(value, (list, tuple)):
            raise ValueError(f"Invalid format value: {value} {self.__class__.__name__} "
                             f"can be not empty list or tuple")

        for id in value:
            if not isinstance(id, int):
                raise ValueError(f"Invalid type ClientID {type(id)}. Expected type int")


class RequestMeta(type):
    def __new__(mcs, name, bases, attrs):
        fields = []
        attributes = list(attrs.items())
        for attr_name, attr_value in attributes:
            if isinstance(attr_value, BaseField):
                fields.append((attr_name, attr_value))

        attrs["fields"] = fields
        return super().__new__(mcs, name, bases, attrs)


class BaseRequest(metaclass=RequestMeta):
    def __init__(self, request_body: Dict[str, Union[List[int], Optional[str]]]):
        self.request_body = request_body

    def _validate_field(self) -> Dict[str, str]:
        validation_errors = dict()
        for field_name, field_ in self.fields:
            try:
                field_request_value = self.request_body.get(field_name)
                setattr(self, field_name, field_request_value)
            except Exception as exc:
                validation_errors[field_name] = str(exc)
        return validation_errors

    def is_valid(self) -> tuple[bool, None] | tuple[bool, dict[str, str]]:
        validation_errors = self._validate_field()
        if not validation_errors:
            return True, None
        return False, validation_errors


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def is_valid(self) -> tuple[bool, Any]:
        validation_errors = self._validate_field()
        if not validation_errors:
            if self.phone and self.email or \
                    self.first_name and self.last_name or \
                    self.gender is not None and self.birthday:
                return True, None
            else:
                return False, "No required fields together"
        return False, validation_errors


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request: MethodRequest):
    if request.is_admin:
        digest = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf-8")).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode("utf-8")).hexdigest()
    if digest == request.token:
        return True
    return False


def handle_interests_request(method_request: MethodRequest, store, context) -> tuple[Any, int] | tuple[dict, int]:
    client_interests_request = ClientsInterestsRequest(request_body=method_request.arguments)
    request_is_valid, errors = client_interests_request.is_valid()
    if not request_is_valid:
        return errors, HTTPStatus.UNPROCESSABLE_ENTITY

    response = {client_id: get_interests(store=store, cid=client_id)
                for client_id in client_interests_request.client_ids}

    context["nclients"] = len(client_interests_request.client_ids)
    return response, HTTPStatus.OK


def handle_score_request(method_request: MethodRequest, store, context) -> Tuple[Dict, Any]:
    online_score_request = OnlineScoreRequest(request_body=method_request.arguments)
    request_is_valid, errors = online_score_request.is_valid()
    if not request_is_valid:
        return errors, HTTPStatus.UNPROCESSABLE_ENTITY

    admin_score_response = 42
    score = admin_score_response if method_request.is_admin else get_score(
        store=store,
        email=online_score_request.email,
        birthday=online_score_request.birthday,
        gender=online_score_request.gender,
        first_name=online_score_request.first_name,
        last_name=online_score_request.last_name,
        phone=online_score_request.phone)

    response = {"score": score}
    context["has"] = [field_val[0] for field_val in online_score_request.fields
                      if online_score_request.__dict__.get(field_val[0]) is not None]

    return response, HTTPStatus.OK


def handle_request_method(method_request: MethodRequest, store, context) -> Tuple[Union[Dict, str], Any]:
    if method_request.method == "clients_interests":
        return handle_interests_request(
            method_request=method_request,
            store=store,
            context=context)
    elif method_request.method == "online_score":
        return handle_score_request(
            method_request=method_request,
            store=store,
            context=context)
    else:
        return "Unknown method", HTTPStatus.UNPROCESSABLE_ENTITY


def method_handler(request: Dict[str, Union[int, Any]], ctx, store):
    print(request, ctx, store)
    method_request = MethodRequest(request_body=request["body"])

    request_method_is_valid, request_method_errors = method_request.is_valid()
    if not request_method_is_valid:
        return request_method_errors, HTTPStatus.UNPROCESSABLE_ENTITY

    if not check_auth(request=method_request):
        return HTTPStatus.FORBIDDEN.phrase, HTTPStatus.FORBIDDEN

    response, code = handle_request_method(
        method_request=method_request,
        context=ctx,
        store=store
    )
    print(response, code)
    return response, code


class HTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = None

    @staticmethod
    def get_request_id(headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def send_response_POST(self, code, response, context):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code is HTTPStatus.OK:
            response = {"response": response, "code": code}
        else:
            try:
                error = HTTPStatus(code).phrase
            except ValueError:
                error = "Unknown Error"
            response = {"error": error, "code": code}

        context.update(response)
        logging.info(context)
        self.wfile.write(json.dumps(response))
        return

    def do_POST(self):
        response, code = dict(), HTTPStatus.OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None

        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
            if request:
                path = self.path.strip("/")
                logging.info(f'{self.path}, {data_string}, {context["request_id"]}')
                if path in self.router:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                else:
                    code = HTTPStatus.NOT_FOUND
        except Exception as error:
            logging.exception("Unexpected error: %s" % error)
            code = HTTPStatus.INTERNAL_SERVER_ERROR

        self.send_response_POST(code, response, context)


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    opts, args = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S')

    server = HTTPServer(("localhost", opts.port), HTTPHandler)
    logging.info(f"Starting server at {opts.port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
