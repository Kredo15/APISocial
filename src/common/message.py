

class LogMessages:
    """Internal log messages"""

    USER_CREATED = "User created: {user_id}"
    USER_LOGGED_IN = "User logged in: {user_id}"
    USER_LOGGED_OUT = "User logged out successfully: {username}"
    USER_SUCCESS_TOKENS = "User created tokens: {user_id}"
    USER_CHANGE_PASSWORD = "User change password: {user_id}"

    USER_ERROR_PASSWORD = "User invalid password: {user_id}"
    USER_ERROR_USERNAME = "invalid username: {username}"
    USER_INACTIVE = "User inactive: {user_id}"
    USER_DUPLICATE = "Duplicate username"

    JWT_DECODE_INVALID = "Invalid decode jwt"
    JWT_INACTIVE = "Not found active refresh token: {user_id}"
    JWT_ERROR_TYPE = "Invalid token type"
