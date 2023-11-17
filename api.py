from flask import Flask, request, abort
# from flask_cors import CORS
# from flask_jwt_extended import create_access_token, JWTManager
from database.show_list_collection import get_showlist, find_show, insert_into_showlist_collection, remove_show_from_list
from database.recorded_shows_collection import get_all_recorded_shows, get_one_recorded_show, insert_new_recorded_show, insert_new_episode, delete_recorded_show
from database.reminder_collection import get_all_reminders, get_one_reminder, create_reminder, edit_reminder, remove_reminder_by_title
from database.users_collection import create_user, check_user_credentials
from aux_methods.helper_methods import get_today_date, valid_reminder_fields
from database.models.RecordedShow import RecordedShow, Season, Episode
from database.models.Reminders import Reminder
from exceptions.DatabaseError import SearchItemAlreadyExistsError, DatabaseError
from config import database_service
from services.tvmaze.tvmaze_api import get_show_data
import json
import os

app = Flask(__name__)
# CORS(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
# JWTManager(app)

# https://www.google.com/search?q=flask-login+react&source=hp&ei=00HmYffoDZKK0AS5sZOYBQ&iflsig=ALs-wAMAAAAAYeZP4_oAIADJhFqmzSf0ow9fxXElhTOc&oq=flask-login+re&gs_lcp=Cgdnd3Mtd2l6EAMYADIFCAAQgAQyBQgAEIAEMgUIABCABDIGCAAQFhAeMgYIABAWEB4yBggAEBYQHjIGCAAQFhAeMgYIABAWEB4yBggAEBYQHjIGCAAQFhAeOhEILhCABBCxAxCDARDHARDRAzoOCC4QgAQQsQMQxwEQowI6CAgAELEDEIMBOgsIABCABBCxAxCDAToICAAQgAQQsQM6CAguELEDEIMBOgsILhCABBDHARCjAjoICC4QgAQQsQM6CwguEIAEEMcBEK8BOg4IABCABBCxAxCDARDJA1AAWNAXYN0jaABwAHgBgAGPBIgB6xuSAQswLjYuMy40LjAuMZgBAKABAQ&sclient=gws-wiz
# https://dev.to/nagatodev/how-to-add-login-authentication-to-a-flask-and-react-application-23i7

@app.route('/show-list', methods=['GET', 'POST'])
def show_list():
    if request.method == 'GET':
        return database_service.get_search_list()
    elif request.method == 'POST':
        if 'show' not in request.json.keys() or 'tvmaze_id' not in request.json.keys():
            return {'message': "Please provide the show's name and the id from TVMaze"}, 400
        show: str = request.json['show']
        tvmaze_id: str = request.json['tvmaze_id']
        try:
            database_service.insert_into_showlist_collection(show)
            new_show_data = get_show_data(show, tvmaze_id)
            recorded_show = RecordedShow.from_database(new_show_data)
            database_service.insert_recorded_show_document(recorded_show)
            return {'message': f'{show} was added to the Search List'}
        except SearchItemAlreadyExistsError as err:
            return {'message': str(err)}, 409
        except DatabaseError as err:
            return {'message': str(err)}, 500
    else:
        abort(405)

@app.route('/guide')
def guide():
    if request.args.get('date'):
        date = request.args.get('date')
        guide = database_service.get_guide_date(date)
        if not guide:
            return {'message': f'No guide data has been found for {date}'}, 404
    else:
        guide = database_service.get_latest_guide()
    return guide.to_dict()

@app.route('/recorded-shows')
def recorded_shows():
    recorded_shows = [recorded_show.to_dict() for recorded_show in database_service.get_all_recorded_shows()]
    return recorded_shows

@app.route('/recorded-show/<string:show>', methods=['GET', 'PUT', 'DELETE'])
def recorded_show(show: str):
    recorded_show = database_service.get_one_recorded_show(show)
    if recorded_show:
        if request.method == 'GET':
            return recorded_show.to_dict()
        if request.method == 'PUT':
            season_query = request.args.get('season')
            episode_query = request.args.get('episode')
            if season_query and episode_query:
                # update episode
                episode = Episode.from_database(request.json)
                database_service.update_episode_in_database(show, season_query, episode)
                return {'message': 'The episode has been updated'}
            elif season_query:
                # add episode to season
                episode = Episode.from_database(request.json)
                database_service.add_new_episode_to_season(recorded_show, season_query, episode)
                return {'message': f'The episode has been added to Season {season_query} of {recorded_show.title}'}
            else:
                # add season
                season = Season.from_database(request.json)
                database_service.add_new_season(recorded_show, season)
                return {'message': f'The season has been added to {recorded_show.title}'}
        if request.method == 'DELETE':
            season_query = request.args.get('season')
            episode_query = request.args.get('episode')
            if season_query and episode_query:
                # delete episode
                database_service.remove_episode_from_season(show, season_query, int(episode_query))
                return {'message': f'Episode {episode_query} has been removed from Season {season_query} of {show}'}
            elif season_query:
                # delete season
                return {'message': 'No action performed'}
            else:
                # delete show
                database_service.delete_recorded_show(show)
                return {'message': f'{show} has been deleted'}
    return {'message': f'A recorded show for {show} could not be found'}, 404

@app.route('/reminders', methods=['GET', 'POST'])
def reminders():
    if request.method == 'GET':
        reminders = [reminder.to_dict() for reminder in database_service.get_all_reminders()]
        return reminders
    if request.method == 'POST':
        reminder = request.json
        show: str = reminder['show']
        show_check = show in database_service.get_search_list()
        reminder_check = database_service.get_one_reminder(show)
        if not show_check:
            return {'message': f'{show} is not being searched for'}, 400
        if reminder_check:
            return {'message': f'A reminder already exists for {show}'}, 409
        new_reminder = Reminder.from_database(reminder)
        try:
            database_service.insert_new_reminder(new_reminder)
            return [reminder.to_dict() for reminder in database_service.get_all_reminders()]
        except DatabaseError as err:
            return {'message': f'An error occurred creating the reminder for {show}', 'error': str(err)}, 500

@app.route('/reminder/<string:show>', methods=['GET', 'PATCH', 'DELETE'])
def reminder(show: str):
    reminder = database_service.get_one_reminder(show)
    if reminder:
        if request.method == 'GET':
            return reminder.to_dict()
        if request.method == 'PATCH':
            body = dict(request.json)
            updated_reminder = Reminder.from_database(body)
            database_service.update_reminder(updated_reminder)
            return updated_reminder.to_dict()
        if request.method == 'DELETE':
            database_service.delete_reminder(show)
            reminders = [reminder.to_dict() for reminder in database_service.get_all_reminders()]
            return {'message': f'The reminder for {show} has been deleted', 'reminders': reminders}
    return {'message': f'A reminder for {show} does not exist'}, 404
   
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
        guide = database_service.get_latest_guide()
        events = [show.to_dict() for show in guide.fta_shows]
        return events

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)