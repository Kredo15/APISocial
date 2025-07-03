from src.auth.services import get_hash_password

test_user_singup = {
    "email": "testemail@example.com",
    "username": "test_user",
    "password": "test_pass"
        }

test_user_add = {
    "email": "testemailogin@example.com",
    "username": "test_user_login",
    "password": get_hash_password("test_pass_login".encode())
}

test_user_singin = {
    "email": "testemailogin@example.com",
    "username": "test_user_login",
    "password": "test_pass_login"
}