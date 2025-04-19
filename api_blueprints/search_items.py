from flask import Blueprint, request
from flask_cors import CORS
from flask_jwt_extended import get_current_user, jwt_required
from sqlalchemy.orm import Session

from database import engine
from database.models import SearchItem, ShowDetails, User

search_items_blueprint = Blueprint("search_items_blueprint", __name__)

CORS(search_items_blueprint)

@search_items_blueprint.route("", methods=['POST'])
@jwt_required()
def add_search_item():
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

    new_search_item = SearchItem(
        show,
        conditions['exact_title_match'],
        conditions['max_season_number'],
        conditions,
        show_details_check.id
    )
    new_search_item.add_search_item(session)
    return new_search_item.to_dict()

@search_items_blueprint.route("/<string:show>", methods=['PUT'])
@jwt_required()
def update_search_item(show: str):
    body = request.json
    if not bool(body):
        return { 'message': "No information was provided to update the search item with" }, 400
    session = Session(engine)
    search_item = SearchItem.get_search_item(show, session)
    if search_item:
        search_item.update_search(body, session)
        return search_item.to_dict()
    return { 'message': f"No search item could be found for '{show}'" }, 404

@search_items_blueprint.route("/<string:show>", methods=['DELETE'])
@jwt_required()
def delete_search_item(show: str):
    session = Session(engine)
    search_item = SearchItem.get_search_item(show, session)
    if search_item:
        search_item.delete_search(session)
        return {'message': f'{show} was deleted from the Search List'}
    return { 'message': f"No search item could be found for '{show}'" }, 404
