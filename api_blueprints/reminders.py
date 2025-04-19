from flask import Blueprint, request
from flask_cors import CORS
from flask_jwt_extended import get_current_user, jwt_required
from sqlalchemy.orm import Session

from database import engine
from database.models import Reminder, ShowDetails, User
from exceptions.DatabaseError import DatabaseError


reminders_blueprint = Blueprint("reminders_blueprint", __name__)
reminder_blueprint = Blueprint("reminder_blueprint", __name__)

CORS(reminders_blueprint)

@reminders_blueprint.route("")
def get_reminders():
    try:
        session = Session(engine)
        reminders = [reminder.to_dict() for reminder in Reminder.get_all_reminders(session)]
        return reminders
    except (KeyError, ValueError) as error:
        return {'message': 'There was a problem retrieving the reminders', 'error': str(error)}, 500

@reminders_blueprint.route("", methods=['POST'])
@jwt_required()
def reminders():
    session = Session(engine)
    body = request.json
    show: str = body['show']
    show_check = ShowDetails.get_show_by_title(show, session)
    reminder_check = Reminder.get_reminder_by_show(show, session)
    if not show_check:
        return {'message': f'{show} is not being searched for'}, 400
    if reminder_check:
        return {'message': f'A reminder already exists for {show}'}, 409
    new_reminder = Reminder(
        show,
        body['alert'],
        body['warning_time'],
        body['occasions'],
        show_check.id
    )
    try:
        new_reminder.add_reminder(session)
        return new_reminder.to_dict()
    except DatabaseError as err:
        return {'message': f'An error occurred creating the reminder for {show}', 'error': str(err)}, 500
    
@reminder_blueprint.route("/<string:show>")
def get_reminder(show: str):
    session = Session(engine)
    reminder = Reminder.get_reminder_by_show(show, session)
    if reminder:
        return reminder.to_dict()
    return {'message': f'A reminder for {show} does not exist'}, 404
    
@reminder_blueprint.route("/<string:show>", methods=['PUT', 'DELETE'])
@jwt_required()
def reminder(show: str):
    session = Session(engine)
    reminder = Reminder.get_reminder_by_show(show, session)
    if reminder:
        if request.method == 'PUT':
            body = dict(request.json)
            updated_reminder = Reminder.get_reminder_by_show(show, session)
            for key in body.keys():
                setattr(updated_reminder, key, body[key])
            return updated_reminder.to_dict()
        if request.method == 'DELETE':
            current_user: User = get_current_user()
            if current_user.role != 'Admin':
                return {'message': f'You are not authorised to delete this reminder. Please make a request to delete it'}, 403
            reminder = Reminder.get_reminder_by_show(show, session)
            reminder.delete_reminder(session)
            reminders = [reminder.to_dict() for reminder in Reminder.get_all_reminders(session)]
            return { 'reminders': reminders }
    return {'message': f'A reminder for {show} does not exist'}, 404
