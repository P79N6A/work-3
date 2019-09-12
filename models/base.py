from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class ORMBase(object):
    __table_args__ = dict(mysql_charset="utf8mb4", )  # 默认utf-8, nullable=False