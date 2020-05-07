def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert 200 == rv.status_code
    print(rv.status)
    assert "text/html; charset=utf-8" == rv.content_type


def test_register(client, app, db):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'aaa', 'password': 'aaa', 'email': 'aaa@exmaple.com'}
    )
    # print(response.headers['Location'])
    # assert 'http://localhost:5000/auth/login' == response.headers['Location']

    with app.app_context():
        assert db.engine.execute(
            "select * from sc_users where username = 'aaa'",
        ).fetchone() is not None
    

def login(client, login_id, password):
    return client.post('/auth/login', data=dict(user=login_id, password=password), follow_redirects=True)


def test_login(client):
    with client:
        # login success test
        rv = login(client, 'admin', 'password')
        assert b'Menu' in rv.data
        # assert session['logged_in']
        # login error test
        rv = login(client, 'none', 'none')
        assert b'Not logged in' in rv.data
        # assert 'logged_in' not in session


"""
['__call__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__',
 '__enter__', '__eq__', '__exit__', '__format__', '__ge__', '__getattribute__',
 '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__',
 '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
 '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__',
 '_cached_json', '_ensure_sequence', '_get_data_for_json',
 '_is_range_request_processable', '_on_close', '_process_range_request',
 '_status', '_status_code', '_wrap_response', 'accept_ranges',
 'access_control_allow_credentials', 'access_control_allow_headers',
 'access_control_allow_methods', 'access_control_allow_origin',
 'access_control_expose_headers', 'access_control_max_age', 'add_etag', 'age',
 'allow', 'autocorrect_location_header', 'automatically_set_content_length',
 'cache_control', 'calculate_content_length', 'call_on_close', 'charset', 'close',
 'content_encoding', 'content_language', 'content_length', 'content_location',
 'content_md5', 'content_range', 'content_security_policy',
 'content_security_policy_report_only', 'content_type', 'data', 'date',
 'default_mimetype', 'default_status', 'delete_cookie', 'direct_passthrough',
 'expires', 'force_type', 'freeze', 'from_app', 'get_app_iter', 'get_data',
 'get_etag', 'get_json', 'get_wsgi_headers', 'get_wsgi_response', 'headers',
 'implicit_sequence_conversion', 'is_json', 'is_sequence', 'is_streamed',
 'iter_encoded', 'json', 'json_module', 'last_modified', 'location',
 'make_conditional', 'make_sequence', 'max_cookie_size', 'mimetype',
 'mimetype_params', 'on_json_loading_failed', 'response', 'retry_after',
 'set_cookie', 'set_data', 'set_etag', 'status', 'status_code', 'stream',
 'vary', 'www_authenticate']
"""
