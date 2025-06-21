from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id):
        self.id = id

def configure_auth(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)