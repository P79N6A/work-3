# coding: UTF-8
import json
# import re

from sqlalchemy.orm import sessionmaker
from tornado.web import RequestHandler

import settings
# from tools.hashids import hashid
from tools.utils import cached_property
from tools.db import get_engine, get_redis_connection
from tools.session import Session


class BaseController(RequestHandler):

    def data_received(self, chunk):
        pass

    @cached_property
    def session(self):
        """Session

        :rtype: tools.session.Session
        """
        session = Session(sessionid=self.session_id, conn=get_redis_connection())
        if not self.session_id:
            self.set_secure_cookie('trade_sid', session.sessionid, domain=settings.COOKIE_DOMAIN)
        return session

    @session.deleter
    def session(self):
        """del session"""
        del self._session  # pylint: disable=no-member

    @cached_property
    def session_id(self):
        """session id, 前后台共用一个sid"""
        return self.get_secure_cookie("trade_sid")

    @cached_property
    def orm_session(self):
        return sessionmaker(bind=get_engine())()

    def on_finish(self):
        if hasattr(self, "_orm_session"):
            self.orm_session.rollback()

    _ARG_DEFAULT = object()

    @cached_property
    def body_data(self):
        """用于angularjs"""
        try:
            return json.loads(self.request.body.decode())
        except ValueError:
            return {}

    def get_argument(self, name, default=_ARG_DEFAULT, strip=True):
        if name in self.body_data:
            return self.body_data[name]

        return super(BaseController, self).get_argument(name, default=default, strip=True)

    @classmethod
    def to_dict(cls, obj, attrs):
        res = {}
        for name in attrs:
            value = getattr(obj, name)
            res[name] = value if value is not None else ""
        return res

    def write(self, chunk):
        if isinstance(chunk, dict):
            chunk = json.dumps(chunk, default=str)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        super().write(chunk)

