import bcrypt
import re
from domain.ports import PasswordServicePort

class BcryptPasswordService(PasswordServicePort):
    def __init__(self, rounds: int = 12):
        self.rounds = rounds

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=self.rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )

    def validate_password_strength(self, password: str) -> bool:
        """
        Validates password strength:
        - At least 8 characters
        - Contains uppercase and lowercase letters
        - Contains at least one digit
        - Contains at least one special character
        """
        if len(password) < 8:
            return False
        
        if not re.search(r'[A-Z]', password):
            return False
        
        if not re.search(r'[a-z]', password):
            return False
        
        if not re.search(r'\d', password):
            return False
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        # Check against common passwords (simplified)
        common_passwords = {
            'password', 'password123', '123456', '12345678',
            'qwerty', 'abc123', 'admin', 'letmein'
        }
        
        if password.lower() in common_passwords:
            return False
        
        return True