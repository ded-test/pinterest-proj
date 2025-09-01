# Ошибки для кодирования JWT


class JWTEncodeError(Exception):
    """Общая ошибка кодирования JWT"""

    pass


class JWTInvalidPayloadError(JWTEncodeError):
    """Ошибка: payload не словарь или не сериализуется"""

    pass


class JWTExpirationError(JWTEncodeError):
    """Ошибка: неверное время жизни токена (exp)"""

    pass


# Ошибки для декодирования JWT


class JWTDecodeError(Exception):
    """Общая ошибка декодирования JWT"""

    pass


class JWTExpiredError(JWTDecodeError):
    """Ошибка: токен просрочен"""

    pass


class JWTInvalidSignatureError(JWTDecodeError):
    """Ошибка: неверная подпись токена"""

    pass


class JWTInvalidTokenError(JWTDecodeError):
    """Ошибка: токен невалидный"""

    pass
