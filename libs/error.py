# coding: utf-8


class STATUS_CODE(object):
    SUCCESS = 100
    VALIDATION_CODE_ERROR = 101
    USER_NOT_EXIST = 102
    VALIDATION_CODE_CHECK_FAILED = 103
    USERNAME_EXIST = 104
    NICK_EXIST = 105
    ERROR_PASSWORD = 106
    USER_ALREADY_ACTIVE = 107
    USERNAME_INVALID = 108
    LOGIN_FAILED = 109
    USER_NOT_ACTIVE = 110
    PHONE_NUM_ERROR = 111           # 手机号错误
    SEND_MESSAGE_ERROR = 112        # 发送验证码失败
    RESEND_MESSAGE_LATER = 113      # 访问频繁，请稍后访问
    ACCOUNT_FORBIDDEN = 114         # 用户被禁止
    PASSWORD_UNSET = 115            # 未设置密码
    PASSWORD_ALREADY_SET = 116      # 已设置密码

    REGIST_LINK_EXPIRED = 201
    REGIST_LINK_INVALID = 202
    REGIST_LINK_USED = 203
    RESET_LINK_EXPIRED = 204
    RESET_LINK_INVALID = 205
    RESET_LINK_USED = 206

    UNKNOWN_DEAL_TYPE = 301
    NOT_PAID_ORDER = 302
    CART_IS_FULL = 303
    ORDER_NOT_EXIST = 304
    ORDER_CLOSED = 305
    UNKNOWN_PAYMENT_CHANNEL = 306
    CALLBACK_FAILED = 307
    PAY_FAILED = 308
    ALREADY_PAID = 309
    CART_DELETED = 310
    DUPLICATE_TRACK = 311
    WAITING_FOR_INVOICE_REQUEST_REVIEW = 322

    TRACK_NOT_EXIST = 401
    NOT_READY_FOR_DOWNLOAD = 402

    TIME_OUT = 504      # 请求超时

    AUTHORIZED_ALREADY = 606    # 已填写授权书

    MISSING_ARGUMENT = 1001


class UserError(Exception):

    def __init__(self, code=200, msg='', http_code=200, **kwargs):
        self.code = code
        self.msg = msg
        self.kwargs = kwargs
        self.http_code = http_code


class PackageError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class WeChatError(UserError):
    pass
