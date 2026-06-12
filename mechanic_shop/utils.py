from jose import jwt, JWTError
from flask import request, jsonify
from functools import wraps
import datetime
import os

SECRET_KEY = os.environ.get('SECRET_KEY')

def encode_token(customer_id):
    payload = {
        'sub':  str(customer_id),
        'iat':  datetime.datetime.now(datetime.timezone.utc),
        'exp':  datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split(' ')[1] if ' ' in auth_header else None

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data        = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            customer_id = data['sub']
        except Exception:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        return f(customer_id, *args, **kwargs)
    return decorated