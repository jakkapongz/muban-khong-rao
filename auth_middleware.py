import json
from datetime import datetime
from functools import wraps
from flask import request, abort, render_template
from flask import current_app
import app as current_app
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, decode_token, verify_jwt_in_request, \
    get_jwt_identity


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token_cookie')
        if not token:
            return render_template('401.html'), 401
        try:
            token_data = decode_token(token)
            exp = token_data['exp']
            token_expire_date = datetime.fromtimestamp(int(exp))
            current_time = datetime.now()
            if token_expire_date < current_time:
                return render_template('401.html'), 401

            current_user = current_app.db_connector.get_user_by_id(token_data['sub']["user_id"])
            if current_user is None:
                return render_template('404.html'), 404
        except Exception as e:
            print(e)
            return render_template('500.html'), 500

        return f(json.loads(current_user), *args, **kwargs)

    return decorated
