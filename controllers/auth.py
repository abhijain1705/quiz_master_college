from flask import Blueprint
from models import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    return 'Login'

@auth.route('/register', methods=['POST'])
def register():
    return 'Register'

@auth.route('/logout', methods=['POST'])
def logout():
    return 'Logout'
        
