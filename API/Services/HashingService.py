import bcrypt

class HashingService:
        
    def hash_bcrypt(self, plain_text: str) -> str:
        return bcrypt.hashpw(plain_text.encode(), bcrypt.gensalt()).decode()


    def check_bcrypt(self, plain_text: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_text.encode(), hashed_password.encode())
        except:
            return False