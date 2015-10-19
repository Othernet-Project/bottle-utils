from __future__ import unicode_literals

try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

import bottle
from webtest import TestApp

from bottle_utils import flash

bottle.debug()
app = bottle.default_app()
app.install(flash.message_plugin)


@app.get('/message')
def get_message():
    return str(bottle.request.message)


@app.post('/message')
def set_message():
    bottle.response.flash('Come on!')


test_app = TestApp(app, cookiejar=CookieJar())

