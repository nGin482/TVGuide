from pymongo import errors, ReturnDocument
from database.mongo import database
import uuid

# Handlers for the reminders

def reminders_collection():
    db = database()
    if db is not None:
        reminders = db.get_collection('Reminders')
        return reminders
    else:
        return []

def get_all_reminders():
    # TODO: DB-001
    try:
        reminders = []
        for reminder in reminders_collection().find():
            reminders.append(reminder)
        return reminders
    except AttributeError:
        return []

def get_one_reminder(show):
    reminders = get_all_reminders()
    
    matched_reminders = list(filter(lambda reminder_object: reminder_object['show'] == show, reminders))
    
    if len(matched_reminders) > 0:
        return {'status': True, 'reminder': matched_reminders[0]}
    else:
        return {'status': False, 'message': 'There is no reminder for this show.'}

def get_reminder_by_id(reminderID: str) -> dict:
    reminders_found = list(filter(lambda reminder_object: reminder_object['reminderID'] == reminderID, get_all_reminders()))
    if len(reminders_found) > 0:
        return {'status': True, 'reminder': reminders_found[0]}
    else:
        return {'status': False, 'message': f'There is no reminder that has the given ID: {reminderID}'}

def create_reminder(reminder_settings):
    
    check_reminder = get_one_reminder(reminder_settings['show'])
    if check_reminder['status']:
        return {'status': False, 'message': 'A reminder has already been set for this show.'}

    if reminder_settings['reminder alert'] == '':
        reminder_settings['reminder alert'] = 'Before'
        reminder_settings['reminder time'] = '3'
    if reminder_settings['reminder alert'] == 'During':
        reminder_settings['reminder time'] = '0'
        
    if 'show' in reminder_settings.keys() and 'reminder time' in reminder_settings.keys() and 'interval' in reminder_settings.keys():
        try:
            reminder_settings['reminderID'] = str(uuid.uuid4())
            reminder = reminders_collection().insert_one(reminder_settings)
        except errors.WriteError as err:
            return {'status': False, 'message': 'An error occurred while setting the reminder for ' + reminder_settings['show'] + '.', 'error': err}
        if reminder.inserted_id:
            return {'status': True, 'message': 'The reminder has been set for ' + reminder_settings['show'] + '.', 'reminder': reminder_settings}
        else:
            return {'status': False, 'message': 'The reminder was not able to be set for ' + reminder_settings['show'] + '.', 'reminder': reminder_settings}
    else:
        return {'status': False, 'message': 'The settings given to create this reminder are invalid because required information is missing.'}

def edit_reminder(reminder):
    from aux_methods import valid_reminder_fields

    check_reminder = get_one_reminder(reminder['show'])
    if check_reminder['status']:
        if reminder['field'] not in valid_reminder_fields():
            return {'status': False, 'message': 'The field given is not a valid reminder field. Therefore, the reminder cannot be updated.'}
        else:
            updated_reminder = reminders_collection().find_one_and_update(
                {'show': reminder['show']},
                {'$set': {reminder['field']: reminder['value']}},
                return_document = ReturnDocument.AFTER
            )
            if updated_reminder[reminder['field']] == reminder['value']:
                return {'status': True, 'message': 'The reminder has been updated.', 'reminder': updated_reminder}
            else:
                return {'status': False, 'message': 'The reminder has not been updated.'}
    else:
        return {'status': False, 'message': 'A reminder has not been set for ' + reminder['show'] + '.'}

def remove_reminder_by_title(show: str):
    check_reminder = get_one_reminder(show)
    if check_reminder['status']:
        deleted_reminder = reminders_collection().find_one_and_delete(
            {'show': show}
        )
        check_again = get_one_reminder(show)
        if not check_again['status']:
            return {'status': True, 'message': 'The reminder for ' + show + ' has been removed.', 'reminder': deleted_reminder}
        else:
            return {'status': False, 'message': 'The reminder for ' + show + ' was not removed.'}
    else:
        return {'status': False, 'message': 'There is no reminder available for ' + show + '.'}

def remove_reminder_by_ID(reminderID: str) -> dict:
    check_reminder = get_reminder_by_id(reminderID)
    if check_reminder['status']:
        deleted_reminder = reminders_collection().find_one_and_delete(
            {'reminderID': reminderID}
        )
        check_again = get_reminder_by_id(reminderID)
        if not check_again['status']:
            return {'status': True, 'message': 'The reminder for ' + check_reminder['reminder']['show'] + ' has been removed.', 'reminder': deleted_reminder}
        else:
            return {'status': False, 'message': 'The reminder for ' + check_reminder['reminder']['show'] + ' was not removed.'}
    else:
        return {'status': False, 'message': 'There is no reminder available for ' + check_reminder['reminder']['show'] + '.'}