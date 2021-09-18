from database.users_collection import get_user, remove_reminder_for_user
from database.reminder_collection import reminders_collection, get_reminder_by_id, remove_reminder_by_ID

def get_reminders_for_user(user: str):
    """Retrieve all Reminder documents allocated to a given user, using the reminderIDs from the User document

    \n
    Args:\n
        user (str): The specified user through which the reminders will be retrieved

    Returns:\n
        list: 'the list of reminder objects set by a user'
    """

    user = get_user(user)
    if user['status']:
        reminderIDs: list = user['user']['reminders']
        user_reminders = []
        
        for reminderID in reminderIDs:
            reminder_status = get_reminder_by_id(reminderID)
            if reminder_status['status']:
                user_reminders.append(reminder_status['reminder'])
        
        return user_reminders
    else:
        return []

def remove_reminder_from_database(user: str, reminderID: str) -> dict:
    """
    Remove a `Reminder` from the database by:\n
    - Removing it from the `User`'s document\n
    - Removing it from the `Reminders` collection
    """
    remove_reminder_for_user(user, reminderID)
    remove_reminder_by_ID(reminderID)