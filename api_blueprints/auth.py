from flask import Blueprint, request
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_current_user, jwt_required
from sqlalchemy.orm import Session

from database import engine
from database.models import User

auth_blueprint = Blueprint("auth_blueprint", __name__)

CORS(auth_blueprint)

@auth_blueprint.route("/register", methods=['POST'])
def register_user():
    body = request.json
    print(body)
    
    session = Session(engine)
    
    check_user = User.search_for_user(body['username'], session)
    if check_user:
        return {'message': 'This username is already in use'}, 409
    
    user = User(body['username'], body['password'])
    user.add_user(session)
    
    return {'message': 'You have successfully been registered'}

@auth_blueprint.route("/login", methods=['POST'])
def login():
    session = Session(engine)
    
    given_credentials = request.json
    user = User.search_for_user(given_credentials['username'], session)
    
    if user and user.check_password(given_credentials['password']):
        return {
            'username': user.username,
            'role': user.role,
            'token': create_access_token(identity=user.username)
        }
    
    return { 'message': 'Incorrect username or password' }, 401
