from flask import Blueprint, request
from flask_cors import CORS
from flask_jwt_extended import get_current_user, jwt_required
from sqlalchemy.orm import Session

from database import engine
from database.models import SearchItem, ShowDetails, ShowEpisode, User
from exceptions.service_error import HTTPRequestError
from services.tvmaze import tvmaze_api
from utils.types.models import TShowData

shows_blueprint = Blueprint("shows_blueprint", __name__)

CORS(shows_blueprint)

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
    return show_data

@shows_blueprint.route("", methods=['POST'])
@jwt_required()
def add_show():
    session = Session(engine)
    body = request.json

    if ShowDetails.get_show_by_title(body['name'], session):
        return { 'message': f"'{body['name']}' is already listed" }, 409

    try:
        tvmaze_details = tvmaze_api.get_show(body['name'])
    except HTTPRequestError as error:
        print(f"Could not find {body['name']} on TVMaze: {error}")
        return { "message": f"Could not find {body['name']} on TVMaze: {error}" }, 404
    show_detail = ShowDetails(
        tvmaze_details['name'],
        tvmaze_details['summary'],
        tvmaze_details['id'],
        tvmaze_details['genres'],
        tvmaze_details['image']['original']
    )
    show_detail.add_show(session)
    
    conditions = body['conditions']
    tvmaze_episodes = tvmaze_api.get_show_episodes(
        tvmaze_details['id'],
        conditions['min_season_number'],
        conditions['max_season_number'],
        True
    )
    show_episodes: list[ShowEpisode] = []
    for episode in tvmaze_episodes:
        try:
            show_episode = ShowEpisode(
                tvmaze_details['name'],
                episode['season_number'],
                episode['episode_number'],
                episode['episode_title'],
                episode['summary'],
                show_id=show_detail.id
            )
            show_episodes.append(show_episode)
        except KeyError as error:
            print("Error:", error)
            print("TVMaze Episode: ", episode)
            return { "message": f"Unable to add an episode for {tvmaze_details['name']}" }, 500
    ShowEpisode.add_all_episodes(show_episodes, session)

    try:
        search_criteria = SearchItem(
            tvmaze_details['name'],
            conditions['exact_title_match'],
            conditions['max_season_number'],
            conditions,
            show_id=show_detail.id
        )
        search_criteria.add_search_item(session)
    except KeyError as error:
        print("Error:", error)
        return { "message": f"Unable to add search criteria for {tvmaze_details['name']}" }, 500

    return {
        "show_name": show_detail.title,
        "show_details": show_detail.to_dict(),
        "show_episodes": [episode.to_dict() for episode in show_episodes],
        "search_item": search_criteria.to_dict() if search_criteria else None,
        "reminder": None
    }

@shows_blueprint.route("/<string:show>", methods=['PUT'])
@jwt_required()
def update_show_detail(show: str):
    session = Session(engine)
    body = request.json

    show_detail = ShowDetails.get_show_by_title(show, session)
    
    if not show_detail:
        return { 'message': f"Unable to find any details for '{show}'" }, 404

    show_detail.update_full_show_details(body, session)

    return show_detail.to_dict()

@shows_blueprint.route("/<string:show>", methods=['DELETE'])
@jwt_required()
def delete_show_detail(show: str):
    session = Session(engine)

    show_detail = ShowDetails.get_show_by_title(show, session)

    user: User = get_current_user()
    if user.role != "Admin":
        return { 'message': f"You do not have permission to delete the details for {show}" }, 403
    
    if not show_detail:
        return { 'message': f"Unable to find any details for '{show}'" }, 404

    show_detail.delete_show(session)

    return '', 204


