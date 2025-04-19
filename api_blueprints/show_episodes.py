from flask import Blueprint, request
from flask_jwt_extended import get_current_user, jwt_required
from flask_cors import CORS
from sqlalchemy.orm import Session

from database import engine
from database.models import ShowEpisode

show_episodes_blueprint = Blueprint("show_episodes_blueprint", __name__)

CORS(show_episodes_blueprint)

@show_episodes_blueprint.route("/<int:id>", methods=['PUT'])
@jwt_required()
def update_show_episode(id: int):
    session = Session(engine)
    episode = ShowEpisode.get_episode_by_id(id, session)
    if episode:
        episode.update_full_episode(request.json, session)
        return episode.to_dict()
    return { 'message': f"This episode could not be found" }, 404

@show_episodes_blueprint.route("/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_show_episode(id: int):
    session = Session(engine)
    episode = ShowEpisode.get_episode_by_id(id, session)
    if episode:
        episode.delete_episode(session)
        return '', 204
    return { 'message': f"This episode could not be found" }, 404