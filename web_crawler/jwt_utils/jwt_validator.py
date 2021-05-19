"""
class used for jwt validator
"""
import jwt
from rest_framework import exceptions

from users.models import Token
from web_crawler import settings

jwt_secret = settings.JWT_SECRET
options = {"verify_exp": True}


def jwt_validator(token):
    try:
        payload = jwt.decode(token, jwt_secret, algorithm="HS256", options=options)
        return payload
    except Exception:
        raise exceptions.AuthenticationFailed


def refresh_token_validator(token):
    try:
        payload = jwt.decode(token, jwt_secret, algorithm="HS256", options=options)
        Token.objects.get(refresh_token=token, is_expired=0)
        return payload
    except Exception:
        return None