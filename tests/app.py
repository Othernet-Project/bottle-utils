from __future__ import unicode_literals

try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

import bottle
from webtest import TestApp

from bottle_utils import ajax, csrf, flash

bottle.debug()
bottle.BaseTemplate.defaults.update({
    'csrf_tag': csrf.csrf_tag
})

app = bottle.default_app()
app.config.update({str('csrf.secret'): 'foo'})
app.install(flash.message_plugin)


# Test handler
@app.get('/ajax_only')
@ajax.ajax_only
def ajax_only_handler():
    return 'success'


@app.get('/csrf_token')
@csrf.csrf_token
def form_view():
    return bottle.template('<form method="POST">{{! csrf_tag() }}</form>')


@app.post('/csrf_token')
@csrf.csrf_protect
def post_view():
    return 'success'


@app.get('/csrf_token_other')
@csrf.csrf_token
def other_form_view():
    return bottle.template('<form method="POST">{{! csrf_tag() }}</form>')


@app.post('/csrf_token_other')
@csrf.csrf_protect
def other_post_view():
    return 'success other'


@app.get('/message')
def get_message():
    return str(bottle.request.message)


@app.post('/message')
def set_message():
    bottle.response.flash('Come on!')


test_app = TestApp(app, cookiejar=CookieJar())

