from flask import Blueprint, request
from flask_cors import CORS
from flask_jwt_extended import get_current_user, jwt_required
from sqlalchemy.orm import Session

from database import engine
from database.models import ShowDetails, User
from exceptions.service_error import HTTPRequestError
from exceptions.DatabaseError import ShowAlreadyExistsError
from services.ShowService import ShowService
from utils.types.models import TShowData

shows_blueprint = Blueprint("shows_blueprint", __name__)

CORS(shows_blueprint, supports_credentials=True)

@shows_blueprint.route("", methods=['GET'])
def shows():
    session = Session(engine)
    shows = ShowDetails.get_all_shows(session)
    show_data: list[TShowData] = []
    for show in shows:
        show_json: TShowData = {
            "show_name": show.title,
            "show_details": show.to_dict(),
            "search_item": show.search.to_dict() if show.search else None,
            "show_episodes": [episode.to_dict() for episode in show.show_episodes],
            "reminder": show.reminder.to_dict() if show.reminder else None
        }
        show_data.append(show_json)
    session.close()
    return show_data

@shows_blueprint.route("", methods=['POST'])
@jwt_required()
def add_show():
    session = Session(engine)
    body = request.json

    show_service = ShowService()

    try:
        show_data = show_service.add_show(body, session)
        session.close()
        return show_data
    except ShowAlreadyExistsError:
        session.close()
        return { 'message': f"'{body['name']}' is already listed" }, 409
    except HTTPRequestError as error:
        session.close()
        return { "message": error.message }, error.status_code

@shows_blueprint.route("/<string:show>", methods=['PUT'])
@jwt_required()
def update_show_detail(show: str):
    session = Session(engine)
    body = request.json

    show_detail = ShowDetails.get_show_by_title(show, session)
    
    if not show_detail:
        session.close()
        return { 'message': f"Unable to find any details for '{show}'" }, 404

    show_detail.update_full_show_details(body, session)
    updated_show_detail_dict = show_detail.to_dict()
    
    session.close()
    return updated_show_detail_dict

@shows_blueprint.route("/<string:show>", methods=['DELETE'])
@jwt_required()
def delete_show_detail(show: str):
    session = Session(engine)

    show_detail = ShowDetails.get_show_by_title(show, session)

    user: User = get_current_user()
    if user.role != "Admin":
        session.close()
        return { 'message': f"You do not have permission to delete the details for {show}" }, 403
    
    if not show_detail:
        session.close()
        return { 'message': f"Unable to find any details for '{show}'" }, 404

    show_detail.delete_show(session)

    session.close()
    return '', 204


