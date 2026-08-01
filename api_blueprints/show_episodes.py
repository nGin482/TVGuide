from flask import Blueprint, request
from flask_jwt_extended import get_current_user, jwt_required
from flask_cors import CORS
from sqlalchemy.orm import Session

from database import engine
from database.models import ShowEpisode

show_episodes_blueprint = Blueprint("show_episodes_blueprint", __name__)

CORS(show_episodes_blueprint, supports_credentials=True)

@show_episodes_blueprint.route("/<int:id>", methods=['PUT'])
@jwt_required()
def update_show_episode(id: int):
    session = Session(engine)
    episode = ShowEpisode.get_episode_by_id(id, session)
    if episode:
        episode.update_full_episode(request.json, session)
        updated_episode_dict = episode.to_dict()
        session.close()
        return updated_episode_dict
    session.close()
    return { 'message': f"This episode could not be found" }, 404

@show_episodes_blueprint.route("/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_show_episode(id: int):
    session = Session(engine)
    episode = ShowEpisode.get_episode_by_id(id, session)
    if episode:
        episode.delete_episode(session)
        session.close()
        return '', 204
    session.close()
    return { 'message': f"This episode could not be found" }, 404