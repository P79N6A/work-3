# coding=utf-8
"""utils package

实现一些业务无关的逻辑
"""

import os
import re
import sys
import fnmatch
import logging
import traceback

from tornado.web import RequestHandler
from tornado.escape import utf8, to_unicode

__all__ = ["cached_property", "ControllerLoader", "SingletonMeta",
           'underline_to_camel', 'camel_to_underline', 'underline_key_decorator']

_MISSING = object()


# pylint: disable=protected-access
class cached_property(property):  # pylint: disable=invalid-name
    """重写property，添加一个缓存机制，使用了_MISSING后，对None值也可以缓存

    设计思路：
    缓存的值写在"_{}".format(attribute_name)里面，
    所有缓存都标记在"_cached_properties"里面。
    想过设计更统一的东东，比如所有缓存的值都写在一个attribute里面，不过似乎写setter的时候会坑
    切忌：除了setter之外，其他代码尽力不要设置"_{}".format(attribute_name)里的值，否则代码会相当confused
    """
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = obj.__dict__.get("_{}".format(self.fget.__name__), _MISSING)  # 手动在__dict__里面查找
        if value is _MISSING:
            value = super(cached_property, self).__get__(obj, objtype)  # 找不到就获取值
            obj.__dict__["_{}".format(self.fget.__name__)] = value  # 写入数据
        return value


class SingletonMeta(type):
    """单例的__metaclass__

    用来实现单例，不知道是否线程安全
    Usage:
        >>> class YouClass(object):
        ...     __metaclass__ = SingletonMeta
        ...
        >>> YouClass() is YouClass()
        True
    """
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls.__instances[cls]


VALID_MODULE_NAME = re.compile(r'[_a-z]\w*\.py$', re.IGNORECASE)


class ControllerLoader(object):  # pylint: disable=too-few-public-methods
    """用于载入所有需要用的controller

    Reference:
        http://hg.python.org/cpython/file/181ced5bf0be/Lib/unittest/loader.py
    """
    __metaclass__ = SingletonMeta

    def __init__(self):
        self._top_level_dir = None

    def discover(self, start_dir, pattern="*", top_level_dir=None, urls_py=None):
        """discover controller from start_dir"""
        if top_level_dir is None:
            top_level_dir = start_dir
        top_level_dir = os.path.abspath(top_level_dir)
        if top_level_dir not in sys.path:
            sys.path.append(top_level_dir)
        self._top_level_dir = top_level_dir

        is_not_importable = False
        if os.path.isdir(os.path.abspath(start_dir)):
            start_dir = os.path.abspath(start_dir)
            if start_dir != top_level_dir:
                is_not_importable = not os.path.isfile(os.path.join(start_dir, '__init__.py'))
        else:
            try:
                __import__(start_dir)
            except ImportError:
                is_not_importable = True
            else:
                the_module = sys.modules[start_dir]
                start_dir = os.path.abspath(os.path.dirname(the_module.__file__))
        if is_not_importable:
            raise ImportError('Start directory is not importable: %r' % start_dir)

        controllers = []
        for _controllers in self._find_controllers(start_dir, pattern):
            controllers.extend(_controllers)

        if urls_py is not None:
            self._print_urls_py(controllers, urls_py)

        return controllers

    @staticmethod
    def _print_urls_py(controllers, urls_py):
        """写一个urls_py，不太健壮的一段代码"""
        with open(urls_py, "w") as f:  # pylint: disable=invalid-name
            f.write("#encoding=utf-8\n")
            f.write("'''\n")
            f.write("Notice the os.path.insert or os.path.append, and the file may fails. It's just a guide.\n")
            f.write("'''\n")
            for controller in controllers:
                uri, obj = controller
                f.write("from {} import {}\n".format(obj.__module__, obj.__name__))
            f.write("\n\n")
            f.write("urls = [\n")
            for controller in controllers:
                uri, obj = controller
                _real_path = sys.modules[obj.__module__].__file__
                import __main__
                _real_path = os.path.relpath(_real_path, __main__.__file__)
                f.write("    (r'{}', {}),  # @file {}\n".format(uri, obj.__name__, _real_path))
            f.write("]\n")

    def _find_controllers(self, start_dir, pattern):  # pylint: disable=too-many-locals
        """在start_dir目录下根据pattern查找controller类"""
        paths = os.listdir(start_dir)
        for path in paths:
            full_path = os.path.join(start_dir, path)  # 当前目录
            if os.path.isfile(full_path):  # 如果是文件，查找文件中的class载入
                if not VALID_MODULE_NAME.match(path):  # 是否为Python文件
                    continue
                if not self._match_path(path, full_path, pattern):
                    continue
                name = self._get_name_from_path(full_path)
                if name == "__init__":
                    continue
                try:
                    module = self._get_module_from_name(name)
                except Exception:  # 类没有正常import，大概需要logging吧 pylint: disable=broad-except
                    logging.warn("Failed to import controller module: %s\n%s", name, traceback.format_exc())
                else:
                    mod_file = os.path.abspath(getattr(module, '__file__', full_path))
                    realpath = os.path.splitext(os.path.realpath(mod_file))[0]
                    fullpath_notetext = os.path.splitext(os.path.realpath(full_path))[0]
                    if realpath.lower() != fullpath_notetext.lower():
                        module_dir = os.path.dirname(realpath)
                        mod_name = os.path.splitext(os.path.basename(full_path))[0]
                        expected_dir = os.path.dirname(full_path)
                        msg = ("%r module incorrectly imported from %r. Expected %r. "
                               "Is this module globally installed?")
                        raise ImportError(msg % (mod_name, module_dir, expected_dir))
                    yield self._load_controllers_from_module(module)
            elif os.path.isdir(full_path):  # 如果是文件夹，迭代进去
                if not os.path.isfile(os.path.join(full_path, '__init__.py')):  # 不是package，不鸟
                    continue
                for controllers in self._find_controllers(full_path, pattern):
                    yield controllers

    @staticmethod
    def _generate_controllers(controller):
        """_generate_controllers"""
        if not issubclass(controller, RequestHandler):
            return {}
        urls = controller.__dict__.get("urls", [])  # 保证urls不是继承来的
        if isinstance(urls, str):
            urls = [urls, ]
        if isinstance(urls, list):
            return [(url, controller) for url in urls if isinstance(url, str)]
        return []

    def _load_controllers_from_module(self, module):
        """返回一个dict，url: RequestHandler"""
        controllers = []
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, RequestHandler):
                controllers.extend(self._generate_controllers(obj))
        return controllers

    @staticmethod
    def _match_path(path, full_path, pattern):  # pylint: disable=unused-argument
        """判断path是否满足pattern"""
        return fnmatch.fnmatch(path, pattern)

    def _get_name_from_path(self, path):
        """根据path返回对应的包名"""
        path = os.path.splitext(os.path.normpath(path))[0]

        _real_path = os.path.relpath(path, self._top_level_dir)
        assert not os.path.isabs(_real_path), "Path must be within the project"
        assert not _real_path.startswith('..'), "Path must be within the project"

        name = _real_path.replace(os.path.sep, '.')
        return name

    @staticmethod
    def _get_module_from_name(name):
        """根据name(字符串)返回对应包"""
        __import__(name)
        return sys.modules[name]


def camel_to_underline(camel_format):
    '''
        驼峰命名格式转下划线命名格式
    '''
    underline_format = ''
    if isinstance(camel_format, str):
        for _s_ in camel_format:
            underline_format += _s_ if _s_.islower() else '_'+_s_.lower()
    return underline_format


def underline_to_camel(underline_format):
    camel_format = ''
    if isinstance(underline_format, str):
        for index, _s_ in enumerate(underline_format.split('_')):
            if index == 0:
                camel_format += _s_
            else:
                camel_format += _s_.capitalize()
    return camel_format


def dict_key_underline_to_camel(in_dict):
    new_dict = []
    for key, value in in_dict.items():
        new_dict[underline_to_camel(key)] = value
    return new_dict


def underline_key_to_camel(in_data):
    new_data = in_data
    if isinstance(in_data, dict):
        new_data = dict()
        for key, value in in_data.items():
            new_data[underline_to_camel(key)] = underline_key_to_camel(value)
    if isinstance(in_data, list):
        new_data = list()
        for value in in_data:
            new_data.append(underline_key_to_camel(value))
    return new_data


def underline_key_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return underline_key_to_camel(result)
    return wrapper


def number2chinese(n, carry=False):
    nums = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    small_units = [(1, ''), (10, '拾'), (100, '佰'), (1000, '仟')]

    if n == 0:
        return nums[0]

    if n >= 10000:
        high_bits = number2chinese(n // 10000, carry=carry) + '万'
        carry = True
    else:
        high_bits = ''

    low_bits = ''
    for base, unit in reversed(small_units):
        if n % (base * 10) == 0:  # 小数部分都是0
            break
        d = (n // base) % 10
        if d == 0:
            low_bits += nums[0] if carry else ''  # 前面有有效位时, 可以加 0
        else:
            low_bits += nums[d] + unit
            carry = True  # 标记有效位

    low_bits = low_bits.replace('零零零', '零')
    low_bits = low_bits.replace('零零', '零')

    return high_bits + low_bits


def test_number2chinese():
    assert number2chinese(0) == '零'
    assert number2chinese(10) == '壹拾'
    assert number2chinese(32) == '叁拾贰'
    assert number2chinese(10000) == '壹万'
    assert number2chinese(10001) == '壹万零壹'
    assert number2chinese(1230) == '壹仟贰佰叁拾'
    assert number2chinese(1203) == '壹仟贰佰零叁'
    assert number2chinese(12000003) == '壹仟贰佰万零叁'
    assert number2chinese(10200003) == '壹仟零贰拾万零叁'
    assert number2chinese(10020003) == '壹仟零贰万零叁'
    assert number2chinese(99) == '玖拾玖'
    assert number2chinese(990) == '玖佰玖拾'
    assert number2chinese(900) == '玖佰'
    assert number2chinese(1020102) == '壹佰零贰万零壹佰零贰'
