from database import create_app, configure_database  
from flask_bcrypt import Bcrypt  
import re  

# Create app and db  
app, db = create_app()  
bcrypt = Bcrypt(app)  

class User(db.Model):  
    __tablename__ = 'forensic_users'  

    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(50), unique=True, nullable=False)  
    email = db.Column(db.String(120), unique=True, nullable=False)  
    password_hash = db.Column(db.String(255), nullable=False)  
    role = db.Column(db.String(50), nullable=False, default='forensic_expert')  
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  

    @staticmethod  
    def validate_email(email):  
        """  
        Validate email format  
        """  
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  
        return re.match(email_regex, email) is not None  

    def set_password(self, password):  
        """  
        Hash and set password  
        """  
        if len(password) < 8:  
            raise ValueError("Password must be at least 8 characters long")  
        
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')  

    def check_password(self, password):  
        """  
        Check if provided password is correct  
        """  
        return bcrypt.check_password_hash(self.password_hash, password)  

    def to_dict(self):  
        """  
        Convert user to dictionary  
        """  
        return {  
            'id': self.id,  
            'username': self.username,  
            'email': self.email,  
            'role': self.role  
        }