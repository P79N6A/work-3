# coding: utf-8

import logging

import tornado.ioloop
from tornado.httpserver import HTTPServer
from tornado.options import options
from tornado.web import Application

import settings
from tools.utils import ControllerLoader


def main():
    handler_list = ControllerLoader().discover("controllers_backend", urls_py='urls')
    logging.info(handler_list)
    application_settings = dict(
        cookie_secret=settings.COOKIE_SECRET,
        cookie_domain=settings.COOKIE_DOMAIN,
        template_path='template',
        static_path=settings.STATIC_DIR,
        xsrf_cookies=False,
        debug=settings.DEBUG,
        autoescape="xhtml_escape",
    )

    application = Application(handler_list, **application_settings)
    server = HTTPServer(application, xheaders=True, max_body_size=1024*1024*2)
    server.bind(options.port)
    server.start(1)

if __name__ == "__main__":
    main()
    tornado.ioloop.IOLoop.instance().start()
