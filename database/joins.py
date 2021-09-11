from database.users_collection import get_user
from database.reminder_collection import get_reminder_by_id

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
        user_reminders = [get_reminder_by_id(reminderID) for reminderID in reminderIDs]
        return user_reminders
    else:
        return []