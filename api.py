from flask import Flask
from flask_restful import Api, Resource, reqparse
from datetime import datetime
from database import get_showlist, find_show, insert_into_showlist_collection, remove_show_from_list
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

if __name__ == '__main__':
    app.run(debug=True)