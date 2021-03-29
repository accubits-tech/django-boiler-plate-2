"""
class used for jwt validator
"""
import jwt
from rest_framework import exceptions

from web_crawler import settings

jwt_secret = settings.JWT_SECRET
options = {"verify_exp": True}


def jwt_validator(token):
    try:
        payload = jwt.decode(token, jwt_secret, algorithm="HS256", options=options)
        return payload
    except Exception:
        raise exceptions.AuthenticationFailed
