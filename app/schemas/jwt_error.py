class JWTPrivateKeyGenerationError(Exception):
    pass


class JWTPrivateKeySaveError(Exception):
    pass


class JWTPublicKeySaveError(Exception):
    pass


class JWTEncodeError(Exception):  # Общая ошибка кодирования JWT
    pass


class JWTInvalidPayloadError(JWTEncodeError):  # Не верный payload
    pass


class JWTAlgorithmError(JWTEncodeError):  # Не поддерживаемый алгоритм
    pass


class JWTKeyError(JWTEncodeError):  # Ошибка ключа
    pass


class JWTExpirationError(JWTEncodeError):  # Ошибка exp(времени жизни токена)
    pass


class JWTDecodeError(Exception):
    pass


class JWTExpiredError(JWTDecodeError):
    pass


class JWTInvalidSignatureError(JWTDecodeError):
    pass


class JWTInvalidTokenError(JWTDecodeError):
    pass


class JWTFormatError(JWTDecodeError):
    pass
