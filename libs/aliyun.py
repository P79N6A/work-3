# coding: utf-8
import json
import logging
import os

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from oss2 import Auth, Bucket
from oss2.exceptions import NoSuchKey

import settings
from common.constants import CONSTANTS
from common.redis import redis
from libs.error import UserError, STATUS_CODE


class MessageSender(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        """单例"""
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.client = AcsClient(settings.ALI_MESSAGE.get('access_key'),
                                settings.ALI_MESSAGE.get('access_key_secret'), 'default')
        self.request = CommonRequest()
        self.request.set_accept_format('json')
        self.request.set_domain('dysmsapi.aliyuncs.com')
        self.request.set_method('POST')
        self.request.set_protocol_type('https')  # https | http
        self.request.set_version('2017-05-25')
        self.request.set_action_name('SendSms')
        self.request.add_query_param('SignName', '库音COOLVOX')  # 签名

    def register_message(self, phone):
        """发送注册短信"""
        key = CONSTANTS.REGIST_KEY.format(phone)

        if 600 - redis.ttl(key) < 60:
            raise UserError(code=STATUS_CODE.RESEND_MESSAGE_LATER)

        self.request.add_query_param('TemplateCode', CONSTANTS.REGISTER_TEMPLATE)
        self.request.add_query_param('PhoneNumbers', phone)
        code = generate_code()  # 生成验证码
        self.request.add_query_param('TemplateParam', json.dumps({'code': code}))
        response = self.client.do_action_with_exception(self.request)

        response = json.loads(response)

        # 验证码发送成功，缓存到redis
        redis.setex(key, CONSTANTS.VERIFY_CODO_TIME_OUT, code)
        return response

    def order_success_message(self, phone, order_id):
        """发送购买成功提醒短信"""
        self.request.add_query_param('TemplateCode', CONSTANTS.ORDER_SUCCESS_TEMPLATE)
        self.request.add_query_param('PhoneNumbers', phone)
        self.request.add_query_param('TemplateParam', json.dumps({'code': order_id}))
        response = self.client.do_action_with_exception(self.request)
        response = json.loads(response)
        logging.info(f'message response ---> {response}')
        return response


class Oss(object):
    def __init__(self, bucket: dict):
        self.auth = Auth(access_key_id=settings.access_key_id, access_key_secret=settings.access_key_secret)
        self.bucket = self._init_bucket(bucket)

    def _init_bucket(self, bucket: dict):
        return Bucket(self.auth, endpoint=bucket.get('endpoint'), bucket_name=bucket.get('bucket'))

    def upload_to_oss(self, key, local_path):
        """
        upload to oss
        :param key: bucket的存储路径
        :param local_path: 本地文件路径
        :return:
        """
        self.bucket.put_object_from_file(key, local_path)
        os.remove(local_path)

    def download_from_oss(self, key, local_path):
        """
        download file from oss
        :param key: bucket中的存储路径
        :param local_path: 下载到本地的路径
        :return:
        """
        try:
            self.bucket.get_object_to_file(key, local_path)
        except NoSuchKey:
            pass

    def is_file_exists(self, file_path):
        """"""
        return self.bucket.object_exists(file_path)
