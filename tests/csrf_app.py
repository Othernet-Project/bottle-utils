from __future__ import unicode_literals

try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

import bottle
from webtest import TestApp

from bottle_utils import csrf

bottle.debug()
bottle.BaseTemplate.defaults.update({
    'csrf_tag': csrf.csrf_tag
})

app = bottle.default_app()
app.config.update({str('csrf.secret'): 'foo'})


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

test_app = TestApp(app, cookiejar=CookieJar())

