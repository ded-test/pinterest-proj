import bcrypt
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime , timedelta , timezone







private_key = rsa.generate_private_key(
    public_exponent = 65537 ,
    key_size = 2048 ,
)

with open('jwt_private.pem' , 'wb') as f:
    f.write(private_key.private_bytes(
        encoding= serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm = serialization.NoEncryption()
    ))

public_key = private_key.public_key()


with open('jwt_public.pem' , 'wb') as f:
    f.write(
        public_key.public_bytes(
            encoding= serialization.Encoding.PEM,
            format = serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def encode_jwt(
        payload : dict,
        private_key : rsa.RSAPrivateKey,
        algorithm = 'RS256',
        expire_min : int = 30
):
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_min)
    to_encode.update(
        exp=int(expire.timestamp()),
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm ,
    )
    return encoded




def decode_jwt(token , public_key , algorithm = ['RS256']):
    
    decoded = jwt.decode(token, public_key, algorithms=algorithm , options={'require' : ['exp']})

    return decoded


def hash_password(
        password : str

)-> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes : bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes , salt)

def validate_password(
        password : str,
        hash_password : bytes,
        
)-> bool:
    return bcrypt.checkpw(password=password.encode(),
                          hashed_password=hash_password,)







