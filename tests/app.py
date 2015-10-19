from __future__ import unicode_literals

try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

import bottle
from webtest import TestApp

from bottle_utils import ajax

bottle.debug()

app = bottle.default_app()
app.config.update({str('csrf.secret'): 'foo'})


# Test handler
@app.get('/ajax_only')
@ajax.ajax_only
def ajax_only_handler():
    return 'success'


test_app = TestApp(app, cookiejar=CookieJar())

