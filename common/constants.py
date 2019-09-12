import collections


__all__ = ['CONSTANTS']


class Constants(collections.UserDict):
    """记录所有常量"""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __getattr__(self, item):
        value = self[item]
        if isinstance(value, dict):
            value = Constants(value)
        return value


# 记录所有redis中用到的key
CACHE_KEY = Constants(
    INDEX_BANNER='index_banner',            # v 首页缓存的key
    INDEX_TAG='index_tag',                  # |
    INDEX_PLAYLIST='index_playlist',        # |
    INDEX_MUSIC='index_music',              # |
    INDEX_CASES='index_cases',              # |
    INDEX_ARTIST='index_artist',            # |
    INDEX_WX_MUSIC='wx:index_music',        # |
    INDEX_WX_PLAYLIST='wx:index_playlist',  # ^ 首页缓存key
    REGIST_KEY='register_{}',               # 验证码的redis key
)


CONSTANTS = Constants(
    VERIFY_CODO_TIME_OUT=600,                               # 短信验证码生存周期
    REGISTER_TEMPLATE='SMS_168285129',                      # 发送注册短信模板
    ORDER_SUCCESS_TEMPLATE='SMS_171113272',                 # 订单短信模板
)


if __name__ == '__main__':
    print(CONSTANTS.INDEX_BANNER)
