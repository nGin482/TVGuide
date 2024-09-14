from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_current_user
from sqlalchemy.orm import Session
import sys
import os

load_dotenv('.env')
from database.database import engine
from database.models import Reminder, SearchItem, ShowDetails, ShowEpisode, User, UserSearchSubscription
from database.models.GuideModel import Guide
from exceptions.DatabaseError import DatabaseError, InvalidSubscriptions
from services.tvmaze.tvmaze_api import get_show_data

app = Flask(__name__, template_folder='build', static_folder='build/static')
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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('build', 'favicon.ico')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('build', 'manifest.json')

# SEARCH LIST
@app.route('/api/show-list', methods=['GET'])
def show_list():
    session = Session(engine)
    return [item.to_dict() for item in SearchItem.get_active_searches(session)]

@app.route('/api/show-list', methods=['POST'])
@jwt_required()
def add_show_list():
    user: User = get_current_user()
    print(user.username)
    body = request.json
    session = Session(engine)
    
    if 'show' not in body or body['show'] == '':
        return { 'message': "Please provide the name of the show to add the Search Item" }, 400
    show, conditions = body['show'], body['conditions']

    show_details_check = ShowDetails.get_show_by_title(show, session)
    search_item_check = SearchItem.get_search_item(show, session)

    if show_details_check is None:
        return { 
            'message': f"No details about '{show}' can be found. Please add details about the show before adding the Search Item"
        }, 400
    if search_item_check:
        return { 'message': f"A Search Item already exists for '{show}'" }, 409

    new_search_item = SearchItem(show, False, conditions)
    new_search_item.add_search_item(session)
    # new_show_data = get_show_data(show, tvmaze_id)

@app.route('/api/show-list/<string:show>', methods=['DELETE'])
@jwt_required()
def delete_search_item(show: str):
    session = Session(engine)
    search_item = SearchItem.get_search_item(show, session)
    if search_item:
        search_item.delete_search(session)
        return {'message': f'{show} was deleted from the Search List'}
    return { 'message': f"No search item could be found for '{show}'" }, 404
        
# GUIDE
@app.route('/api/guide')
def guide():
    from data_validation.validation import Validation
    if request.args.get('date'):
        dates = request.args.get('date').split('/')
        date = datetime(year=int(dates[2]), month=int(dates[1]), day=int(dates[0]))
    else:
        date = Validation.get_current_date()
    guide = Guide(date)
    guide.get_shows()
    return guide.to_dict()

# RECORDED SHOWS
@app.route('/api/recorded-shows')
def recorded_shows():
    session = Session(engine)
    recorded_shows = [show.to_dict() for show in ShowDetails.get_all_shows(session)]
    return recorded_shows

@app.route('/api/recorded-show/<string:show>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def recorded_show(show: str):
    session = Session(engine)
    show_details = ShowDetails.get_show_by_title(show, session)
    if show_details:
        if request.method == 'GET':
            return show_details.to_dict()
        if request.method == 'PUT':
            body: dict = request.json
            for key in body.keys():
                show_details.update_show(key, body[key])
            return { 'show_details': show_details.to_dict() }
        if request.method == 'DELETE':
            current_user: User = get_current_user()
            if current_user.role != 'Admin':
                return { 'message': f"You are not authorised to delete '{show}'. Please make a request to delete it" }, 403
            show_details.delete_show()
            return {'message': f'{show} has been deleted'}
    return {'message': f"Details for '{show}' could not be found"}, 404

# REMINDERS
@app.route('/api/reminders')
def get_reminders():
    try:
        session = Session(engine)
        reminders = [reminder.to_dict() for reminder in Reminder.get_all_reminders(session)]
        return reminders
    except (KeyError, ValueError) as error:
        return {'message': 'There was a problem retrieving the reminders', 'error': str(error)}, 500

@app.route('/api/reminders', methods=['POST'])
@jwt_required()
def reminders():
    session = Session(engine)
    body = request.json
    show: str = body['show']
    show_check = ShowDetails.get_show_by_title(show, session)
    reminder_check = Reminder.get_reminder_by_show(show, session)
    if not show_check:
        return {'message': f'{show} is not being searched for'}, 400
    if reminder_check:
        return {'message': f'A reminder already exists for {show}'}, 409
    new_reminder = Reminder(show, body['alert'], body['warning_time'], body['occasions'])
    try:
        new_reminder.add_reminder(session)
        return {
            'reminders': new_reminder.to_dict()
        }
    except DatabaseError as err:
        return {'message': f'An error occurred creating the reminder for {show}', 'error': str(err)}, 500
    
@app.route('/api/reminder/<string:show>')
def get_reminder(show: str):
    session = Session(engine)
    reminder = Reminder.get_reminder_by_show(show, session)
    if reminder:
        return reminder.to_dict()
    return {'message': f'A reminder for {show} does not exist'}, 404
    
@app.route('/api/reminder/<string:show>', methods=['PUT', 'DELETE'])
@jwt_required()
def reminder(show: str):
    session = Session(engine)
    reminder = Reminder.get_reminder_by_show(show, session)
    if reminder:
        if request.method == 'PUT':
            body = dict(request.json)
            updated_reminder = Reminder.get_reminder_by_show(show, session)
            for key in body.keys():
                setattr(updated_reminder, key, body[key])
            return updated_reminder.to_dict()
        if request.method == 'DELETE':
            current_user: User = get_current_user()
            if current_user.role != 'Admin':
                return {'message': f'You are not authorised to delete this reminder. Please make a request to delete it'}, 403
            reminder = Reminder.get_reminder_by_show(show, session)
            reminder.delete_reminder(session)
            reminders = [reminder.to_dict() for reminder in Reminder.get_all_reminders(session)]
            return { 'reminders': reminders }
    return {'message': f'A reminder for {show} does not exist'}, 404

# USERS
@app.route('/api/user/<string:username>', methods=['GET'])
def get_user(username: str):
    session = Session(engine)
    user = User.search_for_user(username, session)
    if user:
        return user.to_dict()
    return {'message': f'An account with the username {username} could not be found'}, 404

@app.route('/api/users/<string:username>/subscriptions', methods=['PUT'])
@jwt_required()
def edit_user_subscriptions(username: str):
    session = Session(engine)
    user = User.search_for_user(username, session)
    if user:
        current_user: User = get_current_user()
        if current_user.username != username:
            return {'message': "You are not able to update this user's details"}, 403
        body = request.json
        try:
            user_subscription = UserSearchSubscription(user.id, body['search_item_id'])
            user_subscription.add_subscription(session)
            return { 'user': user.to_dict() }
        except InvalidSubscriptions as err:
            return {'message': str(err)}, 400            
    return {'message': f'A user with the username {username} could not be found'}, 404

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
    
@app.route('/api/user/<string:username>/change_password', methods=['POST'])
@jwt_required()
def change_password(username: str):
    current_user: User = get_current_user()
    session = Session(engine)
    user = User.search_for_user(username, session)
    if user and current_user.username == user.username:
        user.change_password(request.json['passowrd'])
        return { 'message': 'Your password has been updated' }
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
            'user': {
                'username': user.username,
                'role': user.role,
                'token': create_access_token(identity=user.username)
            }
        }
    return { 'message': 'Incorrect username or password' }, 401

if __name__ == '__main__':
    if os.getenv('PYTHON_ENV') == 'production':
        host = 'tvguide-ng.fly.dev'
        debug = False
    else:
        host = '0.0.0.0'
        debug = True
    app.run(host=host, port='5000', debug=debug)