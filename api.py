from flask import Flask, request, abort, jsonify
# from flask_cors import CORS
# from flask_jwt_extended import create_access_token, JWTManager
from database.show_list_collection import get_showlist, find_show, insert_into_showlist_collection, remove_show_from_list
from database.recorded_shows_collection import get_all_recorded_shows, get_one_recorded_show, insert_new_recorded_show, insert_new_episode, delete_recorded_show
from database.reminder_collection import get_all_reminders, get_one_reminder, create_reminder, edit_reminder, remove_reminder_by_title
from database.users_collection import create_user, check_user_credentials
from aux_methods.helper_methods import get_today_date, valid_reminder_fields
from config import database_service
# from data_validation.validation import Validation
import json
import os

app = Flask(__name__)
# CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
# JWTManager(app)

# https://www.google.com/search?q=flask-login+react&source=hp&ei=00HmYffoDZKK0AS5sZOYBQ&iflsig=ALs-wAMAAAAAYeZP4_oAIADJhFqmzSf0ow9fxXElhTOc&oq=flask-login+re&gs_lcp=Cgdnd3Mtd2l6EAMYADIFCAAQgAQyBQgAEIAEMgUIABCABDIGCAAQFhAeMgYIABAWEB4yBggAEBYQHjIGCAAQFhAeMgYIABAWEB4yBggAEBYQHjIGCAAQFhAeOhEILhCABBCxAxCDARDHARDRAzoOCC4QgAQQsQMQxwEQowI6CAgAELEDEIMBOgsIABCABBCxAxCDAToICAAQgAQQsQM6CAguELEDEIMBOgsILhCABBDHARCjAjoICC4QgAQQsQM6CwguEIAEEMcBEK8BOg4IABCABBCxAxCDARDJA1AAWNAXYN0jaABwAHgBgAGPBIgB6xuSAQswLjYuMy40LjAuMZgBAKABAQ&sclient=gws-wiz
# https://dev.to/nagatodev/how-to-add-login-authentication-to-a-flask-and-react-application-23i7

@app.route('/show-list', methods=['GET', 'PUT'])
def show_list():
    if request.method == 'GET':
        return database_service.get_search_list()
    elif request.method == 'PUT':
        insert_status = insert_into_showlist_collection(request.json['show'])
        if insert_status['status']:
            return {'show': request.json['show'], 'message': insert_status['message']}
        else:
            if 'searched' in insert_status['message']:
                return {'show': request.json['show'], 'message': insert_status['message']}, 409
            else:
                return {'show': request.json['show'], 'message': insert_status['message']}, 500
    else:
        abort(405)

@app.route('/guide')
def guide():
    guide = database_service.get_latest_guide()
    return guide.to_dict()

@app.route('/recorded-shows')
def recorded_shows():
    recorded_shows = [recorded_show.to_dict() for recorded_show in database_service.get_all_recorded_shows()]
    return recorded_shows

@app.route('/recorded-show/<string:show>', methods=['GET', 'PUT', 'DELETE'])
def recorded_show(show: str):
    if request.method == 'GET':
        recorded_show = database_service.get_one_recorded_show(show)
        if recorded_show:
            return recorded_show.to_dict()
        return {'message': f'{show} was not found'}, 404
    if request.method == 'PUT':
        # add episode to Recorded Show
        recorded_show = get_one_recorded_show(show)
        if not recorded_show['status']:
            return {'status': False, 'message': recorded_show['message']}, 404
        else:
            body = request.json['show']
            episode_insert_status = insert_new_episode(body)
            if episode_insert_status['status']:
                del episode_insert_status['result']['_id']
                return episode_insert_status
            else:
                return episode_insert_status
    if request.method == 'DELETE':
        recorded_show = get_one_recorded_show(show)
        if not recorded_show['status']:
            return {'status': False, 'message': recorded_show['message']}, 404
        else:
            deleted_show = delete_recorded_show(show)
            del deleted_show['show']['_id']
            if not deleted_show['status']:
                return {'status': False, 'message': deleted_show['message']}, 404
            else:
                return deleted_show

@app.route('/reminders')
def reminders():
    if request.method == 'GET':
        reminders = [reminder.to_dict() for reminder in database_service.get_all_reminders()]
        return reminders
    if request.method == 'PUT':
        reminder_body = request.json['reminder']
        reminder_created = create_reminder(reminder_body)
        if reminder_created['status']:
            del reminder_created['reminder']['_id']
            return reminder_created
        else:
            return reminder_created, 409

@app.route('/reminder/<string:show>', methods=['GET', 'PATCH', 'DELETE'])
def reminder(show: str):
    if request.method == 'GET':
        reminder = database_service.get_one_reminder(show)
        if reminder:
            return reminder.to_dict()
        return {'message': f'A reminder for {show} could not be found'}
    if request.method == 'PATCH':
        reminder_check = get_one_reminder(show)
        if not reminder_check['status']:
            return {'status': False, 'message': reminder_check['message']}, 404
        body = request.json
        if body['field'] in valid_reminder_fields():
            update_reminder_object = {
                'show': show,
                'field': body['field'],
                'value': body['value']
            }
            update_reminder_status = edit_reminder(update_reminder_object)
            if update_reminder_status['status']:
                del update_reminder_status['reminder']['_id']
                return update_reminder_status
            else:
                return update_reminder_status, 500
        return {'status': False, 'message': 'Unable to update this reminder because the field given to update is not valid.'}, 400
    if request.method == 'DELETE':
        reminder_check = get_one_reminder(show)
        if not reminder_check['status']:
            return {'message': 'There is no reminder set for ' + show + '.'}, 404
        remove_reminder_status = remove_reminder_by_title(show)
        if not remove_reminder_status['status']:
            return remove_reminder_status, 500
        del remove_reminder_status['reminder']['_id']
        return remove_reminder_status
   
@app.route('/auth/register', methods=['PUT'])
def registerUser():
    if request.method == 'PUT':
        new_user = request.json
        print(new_user)
        insert_new_user = create_user(new_user)
        if insert_new_user['status']:
            return insert_new_user
        else:
            return insert_new_user, 500

@app.route('/auth/login', methods=['POST'])
def login():
    if request.method == 'POST':
        given_credentials = request.json
        cred_check = check_user_credentials(given_credentials)
        if cred_check['status']:
            return {
                'user': given_credentials['username'],
                'searchList': cred_check['user']['searchList'],
                'reminders': cred_check['user']['reminders'],
                'token': create_access_token(identity=given_credentials['username']),
                'role': cred_check['user']['role']
            }
        else:
            return {'status': False, 'message': 'Incorrect username or password'}, 401

@app.route('/events')
def events():
    if request.method == 'GET':
        try:
            with open('log/events.json') as fd:
                events = json.load(fd)
            return events
        except FileNotFoundError:
            return {'message': 'The logging information can not be retrieved.'}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)