import bcrypt


def get_hash_password(
    password: str,
) -> str:
    pwhash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return pwhash.decode('utf-8')
