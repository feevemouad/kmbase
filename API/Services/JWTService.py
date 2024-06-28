import jwt 
from jwt import DecodeError, InvalidSignatureError
from time import time
from typing import Union


class JWTService:
    expires_in_seconds = 1800 # 30 minutes # TODO: change to 30 days or something
    signing_algorithm = "HS256"

    def __init__(self, signing_key: str, expires_in_seconds: int = 1800):
        self.signing_key = signing_key
        self.expires_in_seconds = expires_in_seconds

    def generate(self, data: dict, expires_in_seconds: int = expires_in_seconds) -> Union[str, None]:
        try:
            
            curr_unix_epoch = int(time())
            data['iat'] = curr_unix_epoch

            if isinstance(expires_in_seconds, int):
                data['exp'] = curr_unix_epoch + expires_in_seconds

            token = jwt.encode(payload=data, key=self.signing_key, algorithm=self.signing_algorithm)

            if type(token) == bytes:
                token = token.decode('utf8')  # Needed for some versions of PyJWT

            return token
        except BaseException as e:
            print(e)
            return None

    def is_valid(self, token: str, verify_time: bool = True) -> bool:
        try:
            payload = self.get_payload(token)

            if payload is None:
                return False

            if verify_time and 'exp' in payload and payload['exp'] < int(time()):
                return False

            return True
        except:
            return False

    def get_payload(self, token: str):
        try:
            payload = jwt.decode(jwt=token, key=self.signing_key, algorithms=[self.signing_algorithm])
            return payload
        except InvalidSignatureError as e:
            print(e)
            return False
        except DecodeError as e:
            print(e)
            return False
