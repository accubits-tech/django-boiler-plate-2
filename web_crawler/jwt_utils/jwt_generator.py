from datetime import datetime, timedelta

import jwt

FORMAT = "%Y-%m-%d %H:%M:%S"
ALGORITHM = "HS256"


def jwt_generator(user_id, jwt_secret, jwt_ttl, token_type, is_admin):
    current_time = datetime.now()
    time = current_time.strftime(FORMAT)
    actual_exp = datetime.strptime(time, FORMAT)

    if jwt_ttl >= 0:
        exp_time = current_time + timedelta(milliseconds=jwt_ttl)
        exp_at = exp_time.strftime(FORMAT)
        actual_exp = datetime.strptime(exp_at, FORMAT)
    payload = {
        "user_id": user_id,
        "is_admin": is_admin,
        "type": token_type,
        "issued_at": time,
        "exp": actual_exp.timestamp(),
    }
    jwt_token = jwt.encode(payload, jwt_secret, ALGORITHM)
    return jwt_token.decode()
