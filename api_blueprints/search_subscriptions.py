from flask import Blueprint, request
from flask_cors import CORS
from flask_jwt_extended import get_current_user, jwt_required
from sqlalchemy.orm import Session

from database import engine
from database.models import SearchItem, User, UserSearchSubscription
from exceptions.DatabaseError import InvalidSubscriptions

search_subscription_blueprint = Blueprint("search_subscription_blueprint", __name__)

CORS(search_subscription_blueprint, supports_credentials=True)

@search_subscription_blueprint.route("", methods=['GET'])
def get_user_subscriptions(username: str):
    session = Session(engine)
    user = User.search_for_user(username, session)
    if user:
        viewed_user = User.search_for_user(username, session)
        user_subscriptions = UserSearchSubscription.get_user_subscriptions(session, viewed_user.id)
        session.close()
        return [subscription.to_dict() for subscription in user_subscriptions] 
    session.close()          
    return {'message': f'A user with the username {username} could not be found'}, 404

@search_subscription_blueprint.route("", methods=['POST'])
@jwt_required()
def add_user_subscriptions(username: str):
    session = Session(engine)
    user = User.search_for_user(username, session)
    if user:
        current_user: User = get_current_user()
        if current_user.username != username:
            session.close()
            return {'message': "You are not able to update this user's details"}, 403
        body: list[str] = request.json
        try:
            user_subscriptions: list[UserSearchSubscription] = []
            for show in body:
                search_item = SearchItem.get_search_item(show, session)
                user_subscriptions.append(UserSearchSubscription(user.id, search_item.id))
            UserSearchSubscription.add_subscription_list(user_subscriptions, session)
            user_dict = user.to_dict()
            session.close()
            return user_dict
        except InvalidSubscriptions as err:
            session.close()
            return {'message': str(err)}, 400  
    session.close()          
    return {'message': f'A user with the username {username} could not be found'}, 404

@search_subscription_blueprint.route("/<string:subscription_id>", methods=['DELETE'])
@jwt_required()
def delete_user_subscription(username: str, subscription_id: str):
    session = Session(engine)
    subscription = UserSearchSubscription.get_subscription_by_id(subscription_id, session)
    if not subscription:
        session.close()
        return { 'message': f'This subscription could not be found' }, 404
    if not subscription.user:
        session.close()
        return { 'message': f'Unable to find the user account' }, 400
    if not subscription.search_item:
        session.close()
        return { 'message': f'This search item does not exist' }, 400
    try:
        subscription.remove_subscription(session)
        session.close()
        return "", 204
    except InvalidSubscriptions as err:
        session.close()
        return {'message': str(err)}, 400 
