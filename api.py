from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from datetime import datetime
from database import (get_showlist, find_show, insert_into_showlist_collection, remove_show_from_list,
    get_all_recorded_shows, get_one_recorded_show, insert_new_recorded_show, delete_recorded_show,
    get_all_reminders, get_one_reminder)
import json

app = Flask(__name__)
api = Api(app)

show_list_args = reqparse.RequestParser()
show_list_args.add_argument('show', type=str, help='A show needs to be given to add to the list.', required=True)

class ShowList(Resource):
    def get(self):
        show_list = get_showlist()
        if len(show_list) == 0:
            return {'message': 'There are no shows being searched for.'}, 404
        else:
            return show_list
            
    def put(self):
        request_args = show_list_args.parse_args()
        insert_status = insert_into_showlist_collection(request_args['show'])
        if insert_status['status']:
            return {'show': request_args['show'], 'message': insert_status['message']}
        else:
            if 'searched' in insert_status['message']:
                return {'show': request_args['show'], 'message': insert_status['message']}, 409
            else:
                return {'show': request_args['show'], 'message': insert_status['message']}, 500
api.add_resource(ShowList, '/show-list')

class SingleShowFromList(Resource):
    def get(self, show):
        print(show)
        show_found = find_show(show)
        if show_found['status']:
            return find_show(show)['show']
        else:
            return {'show': show, 'message': show_found['message']}, 404
            
    def delete(self, show):
        remove_status = remove_show_from_list(show)
        if remove_status['status']:
            return {'show': show, 'message': remove_status['message']}
        else:
            return {'show': show, 'message': remove_status['message']}, 500
api.add_resource(SingleShowFromList, '/show-list/<string:show>')

class Guide(Resource):
    def get(self):
        try:
            filename = 'today_guide/' + datetime.strftime(datetime.today(), '%d-%m-%Y') + '.json'
            with open(filename) as fd:
                guide = json.load(fd)
            return guide
        except FileNotFoundError:
            return {'status': False, 'message': 'There is no guide data to retrieve'}, 404
api.add_resource(Guide, '/guide')

class RecordedShows(Resource):
    def get(self):
        recorded_shows = get_all_recorded_shows()
        if len(recorded_shows) == 0:
            return {'status': False, 'message': 'There is not any data about shows tracked.'}, 404
        else:
            for show in recorded_shows:
                del show['_id']
            return recorded_shows
api.add_resource(RecordedShows, '/recorded-shows')

class RecordedShow(Resource):
    def get(self, show):
        recorded_show = get_one_recorded_show(show)
        if not recorded_show['status']:
            return {'status': False, 'message': recorded_show['message']}, 404
        else:
            del recorded_show['show']['_id']
            return recorded_show

    def delete(self, show):
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
api.add_resource(RecordedShow, '/recorded-show/<string:show>')

class Reminders(Resource):
    def get(self):
        reminders = get_all_reminders()
        if len(reminders) == 0:
            return {'status': False, 'message': 'There are no reminders currently available'}, 404
        for reminder in reminders:
            del reminder['_id']
        return reminders
api.add_resource(Reminders, '/reminders')

class Reminder(Resource):
    def get(self, show):
        reminder = get_one_reminder(show)
        if not reminder['status']:
            return {'status': False, 'message': reminder['message']}, 404
        del reminder['reminder']['_id']
        return reminder['reminder']
api.add_resource(Reminder, '/reminder/<string:show>')
        

if __name__ == '__main__':
    app.run(debug=True)