from dotenv import load_dotenv
from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_current_user
from sqlalchemy.orm import Session
from werkzeug.exceptions import HTTPException
import json
import os

load_dotenv('.env')
from api_blueprints import (
    guide_blueprint,
    reminder_blueprint,
    reminders_blueprint,
    search_items_blueprint,
    search_subscription_blueprint,
    shows_blueprint,
    show_episodes_blueprint,
)
from database import engine
from database.models import User

app = Flask(__name__, template_folder='frontend/build', static_folder='frontend/build/assets')
CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
jwt = JWTManager(app)

# https://www.google.com/search?q=flask-login+react&source=hp&ei=00HmYffoDZKK0AS5sZOYBQ&iflsig=ALs-wAMAAAAAYeZP4_oAIADJhFqmzSf0ow9fxXElhTOc&oq=flask-login+re&gs_lcp=Cgdnd3Mtd2l6EAMYADIFCAAQgAQyBQgAEIAEMgUIABCABDIGCAAQFhAeMgYIABAWEB4yBggAEBYQHjIGCAAQFhAeMgYIABAWEB4yBggAEBYQHjIGCAAQFhAeOhEILhCABBCxAxCDARDHARDRAzoOCC4QgAQQsQMQxwEQowI6CAgAELEDEIMBOgsIABCABBCxAxCDAToICAAQgAQQsQM6CAguELEDEIMBOgsILhCABBDHARCjAjoICC4QgAQQsQM6CwguEIAEEMcBEK8BOg4IABCABBCxAxCDARDJA1AAWNAXYN0jaABwAHgBgAGPBIgB6xuSAQswLjYuMy40LjAuMZgBAKABAQ&sclient=gws-wiz
# https://dev.to/nagatodev/how-to-add-login-authentication-to-a-flask-and-react-application-23i7

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    session = Session(engine)
    return User.search_for_user(jwt_data['sub'], session)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shows')
def shows_page():
    return render_template('index.html')

@app.route('/shows/<string:show>')
def show_page(show: str):
    return render_template('index.html')

@app.route('/shows/<string:show>/episodes')
def show_episodes_page(show: str):
    return render_template('index.html')

@app.route('/shows/<string:show>/search')
def show_search_page(show: str):
    return render_template('index.html')

@app.route('/shows/<string:show>/reminder')
def show_reminder_page(show: str):
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('index.html')

@app.route('/profile/<string:user>')
def profile_page(user: str):
    return render_template('index.html')

@app.route('/profile/<string:user>/settings')
def profile_settings_page(user: str):
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('frontend', 'favicon.ico')


app.register_blueprint(guide_blueprint, url_prefix="/api/guide")
app.register_blueprint(reminder_blueprint, url_prefix="/api/reminder")
app.register_blueprint(reminders_blueprint, url_prefix="/api/reminders")
app.register_blueprint(search_items_blueprint, url_prefix="/api/search-item")
app.register_blueprint(
    search_subscription_blueprint,
    url_prefix="/api/users/<string:username>/subscriptions"
)
app.register_blueprint(shows_blueprint, url_prefix="/api/shows")
app.register_blueprint(show_episodes_blueprint, url_prefix="/api/show-episode") 


# USERS
@app.route('/api/user/<string:username>', methods=['GET'])
def get_user(username: str):
    session = Session(engine)
    user = User.search_for_user(username, session)
    if user:
        return user.to_dict()
    return {'message': f'An account with the username {username} could not be found'}, 404

@app.route('/api/user/<string:username>/promote', methods=['PATCH'])
@jwt_required()
def promote_user(username: str):
    session = Session(engine, expire_on_commit=False)
    current_user: User = get_current_user()
    if current_user.role == 'Admin':
        user = User.search_for_user(username, session)
        if user:
            user.promote_role()
            session.commit()
            session.close()
            return '', 204
        session.close()
        return { 'message': f"Unable to find the user '{username}'" }, 404
    return { 'message': 'You are not authorised to promote this user to an admin role' }, 403
    
@app.route('/api/user/<string:username>/change_password', methods=['PUT'])
@jwt_required()
def change_password(username: str):
    current_user: User = get_current_user()
    session = Session(engine)
    user = User.search_for_user(username, session)
    if user and current_user.username == user.username:
        user.change_password(request.json['password'])
        session.commit()
        return user.to_dict()
    return { 'message': "You are not authorised to change this user's password" }, 403

@app.route('/api/user/<string:username>', methods=['DELETE'])
@jwt_required()
def delete_user(username: str):
    session = Session(engine)
    current_user: User = get_current_user()
    user = User.search_for_user(username, session)
    if current_user.username == username:
        user.delete_user(session)
        return { 'message': 'Your account has been deleted' }
    elif current_user.role == 'Admin':
        if user:
            user.delete_user(session)
            return { 'message': 'The account has been deleted' }
        else:
            return {'message': f"An account with the username '{username}' could not be found"}, 404
    else:
        return { 'message': 'You are not authorised to delete this user account' }

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    body = request.json
    session = Session(engine)
    check_user = User.search_for_user(body['username'], session)
    if check_user:
        return {'message': 'This username is already in use'}, 409
    print(body)
    user = User(body['username'], body['password'])
    user.add_user(session)
    return {'message': 'You have successfully been registered'}

@app.route('/api/auth/login', methods=['POST'])
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

@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

if __name__ == '__main__':
    if os.getenv('PYTHON_ENV') == 'production':
        host = 'tvguide-ng.fly.dev'
        debug = False
    else:
        host = '0.0.0.0'
        debug = True
    app.run(host=host, port='5000', debug=debug)