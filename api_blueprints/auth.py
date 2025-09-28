from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies
)
from sqlalchemy.orm import Session

from database import engine
from database.models import User

auth_blueprint = Blueprint("auth_blueprint", __name__)

CORS(auth_blueprint, supports_credentials=True)

@auth_blueprint.route("/register", methods=['POST'])
def register_user():
    body = request.json
    
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
        response = jsonify({
            "username": user.username,
            "role": user.role,
        })

        access_token = create_access_token(user.username)
        refresh_token = create_refresh_token(user.username)
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        return response
    
    return { 'message': 'Incorrect username or password' }, 401
