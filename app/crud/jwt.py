from app.core.logger_config import get_logger
from app.core.dependencies import get_db_session, get_redis
from app.security.jwt import jwt_manager

class JWTCRUD():
    def create_token(user: dict):
        try: 
            access_payload = {"sub": str(user.id), "username": user.username}
            refresh_payload = {"sub": str(user.id), "token_type": "refresh"}

            access_token = jwt_manager.create_access_token(access_payload)
            refresh_token = jwt_manager.create_refresh_token(refresh_payload)
            
        
    def saving_token(token:str):
        try:
            
        