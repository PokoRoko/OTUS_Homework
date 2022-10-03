#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Optional, Dict, Union, List, Tuple

from dateutil.relativedelta import relativedelta

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500

ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}

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
    """
    Base class fields
    """

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
            json.dumps(value)
        except TypeError:
            raise ValueError(f"{self.__class__.__name__} invalid value type, can be dict or json")


class EmailField(CharField):
    def _validate(self, value: str) -> None:
        super()._validate(value)
        if "@" not in value:
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
            self.date = datetime.datetime.strptime(value, "%d.%m.%Y")


class BirthDayField(DateField):
    def _validate(self, value: str) -> None:
        super()._validate(value)
        if self.date < datetime.datetime.now() - relativedelta(years=MAX_AGE):
            raise ValueError(f"Invalid date of birth. Date cannot be more than {MAX_AGE} years ago")


class GenderField(BaseField):
    def _validate(self, value: int) -> None:
        super()._validate(value)
        if value is not None and value not in GENDERS:
            raise ValueError(f"Value can be is one {GENDERS}")


class ClientIDsField(BaseField):
    def __init__(self, required: bool, nullable: bool = False):

        super().__init__(required, nullable)

    def _validate(self, value: Optional[List[int]]) -> None:

        super()._validate(value)
        if not value or not isinstance(value, (list, tuple)):
            raise ValueError(f"Invalid format value: {value} {self.__class__.__name__} "
                             f"can be not empty list or tuple")

        for id in value:
            if not isinstance(id, int):
                raise ValueError(f"Invalid type ClientID {type(id)}. Expected type int")


def method_handler(request, ctx, store):
    pass


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

    def _validate_form(self) -> Dict[str, str]:
        validation_errors = dict()
        for field_name, field_ in self.fields:
            try:
                field_request_value = self.request_body.get(field_name)
                setattr(self, field_name, field_request_value)
            except Exception as exc:
                validation_errors[field_name] = str(exc)
        return validation_errors

    def is_valid(self) -> Tuple[bool, Optional[str]]:
        validation_errors = self._validate_form()
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

    def is_valid(self) -> Tuple[bool, Optional[str]]:

        """
        Checks if request is valid.
        Request is valid if every single field is valid
        and at least one pair of fields (phone-mail, first_name-last_name, gender-birthday)
        is not empty
        :return: boolean if request is valid and error text if it is not valid
        """

        validation_errors = self._validate_form()
        if not validation_errors:
            if self.phone and self.email:
                return True, None
            elif self.first_name and self.last_name:
                return True, None
            elif self.gender is not None and self.birthday:
                return True, None
            return False, "No required fields found together"

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
            (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf-8")
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            (request.account + request.login + SALT).encode("utf-8")
        ).hexdigest()
    if digest == request.token:
        return True

    return False

class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
