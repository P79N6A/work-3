from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, text, SMALLINT
from sqlalchemy.sql.functions import current_timestamp

from models.base import ORMBase


class AccessID(ORMBase):
    """用来登录的账户信息, 与account表多对一"""
    __tablename__ = 'access_ids'

    id = Column(Integer, primary_key=True, nullable=False)
    access_name = Column(String(64), nullable=False, default='')
    sign = Column(Integer, nullable=False, default=1)  # 1:手机号登录  2: 微信open_id登录  3: union_id登录
    account_id = Column(Integer)
    json_format = Column(Text)


class Account(ORMBase):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(64), nullable=False, default='')  # 冗余字段,减少join查询
    nickname = Column(String(64), nullable=False, default='')
    hashed_password = Column(String(128), nullable=False, default='')
    password_salt = Column(String(64), nullable=False, default='')
    active = Column(Integer, nullable=False, default=0)
    last_login_ip = Column(String(128), nullable=False, default='', )
    created_datetime = Column(TIMESTAMP, server_default=current_timestamp())
    last_login_time = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class Admin(ORMBase):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(64), nullable=False, default='', unique=True, )
    hashed_password = Column(String(128), nullable=False, )
    password_salt = Column(String(64), nullable=False, )
    level = Column(SMALLINT, nullable=False, default=0, )
    forbidden = Column(SMALLINT, nullable=False, default=0)
    created_datetime = Column(TIMESTAMP, server_default=current_timestamp())
    last_login_time = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
