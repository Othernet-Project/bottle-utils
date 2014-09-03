try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

import bottle
from webtest import TestApp

from bottle_utils import ajax, csrf

bottle.debug()
bottle.BaseTemplate.defaults.update({
    'csrf_tag': csrf.csrf_tag
})

app = bottle.default_app()
app.config.update({'csrf.secret': 'foo'})


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


test_app = TestApp(app, cookiejar=CookieJar())

