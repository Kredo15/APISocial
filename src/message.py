

class LogMessages:
    """Internal log messages"""

    USER_CREATED = "User created: {user_id}"
    USER_LOGGED_IN = "User logged in: {user_id}"
    USER_LOGGED_OUT = "User logged out successfully: {username}"
    USER_SUCCESS_TOKENS = "User created tokens: {user_id}"
    USER_CHANGE_PASSWORD = "User change password: {user_id}"
    USER_RESET_PASSWORD = "User reset password: {user_id}"
    USER_CONFIRMED = "User confirmed email: {user_id}"

    USER_ERROR_PASSWORD = "User invalid password: {user_id}"
    USER_ERROR_USERNAME = "invalid username: {username}"
    USER_INACTIVE = "User inactive: {user_id}"
    USER_DUPLICATE = "Duplicate username"
    USER_ERROR_CONFIRMED = "Token error during confirmation email: {user_id}"

    JWT_DECODE_INVALID = "Invalid decode jwt"
    JWT_INACTIVE = "Not found active refresh token: {user_id}"
    JWT_ERROR_TYPE = "Invalid token type"

    EMAIL_SUCCESS_SEND = "Email successfully sent to {to_email}"
    EMAIL_ERROR_SEND = "Error sending email to {to_email}: {e}"

    PROFILE_NOT_FOUND = "Profile {profile_id} not found to user: {user_id}"
