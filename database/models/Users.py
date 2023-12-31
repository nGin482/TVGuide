import bcrypt

from exceptions.DatabaseError import InvalidSubscriptions

class User:


    def __init__(self, username: str, password: str, show_subscriptions: list[str], reminder_subscriptions: list[str], role: str):
        self.username = username
        self.password = password
        self.show_subscriptions = show_subscriptions
        self.reminder_subscriptions = reminder_subscriptions
        self.role = role

    @classmethod
    def from_database(cls, user_details: dict[str, str | list[str]]):
        username: str = user_details['username']
        password: str = user_details['password']
        show_subscriptions: list[str] = user_details['show_subscriptions']
        reminder_subscriptions: list[str] = user_details['reminder_subscriptions']
        role: str = user_details['role']

        return cls(username, password, show_subscriptions, reminder_subscriptions, role)
    
    @classmethod
    def register_new_user(cls, username: str, password: str, show_subscriptions: list[str], reminder_subscriptions: list[str]):
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(14))

        return cls(username, hashed_password.decode(), show_subscriptions, reminder_subscriptions, 'Standard')
    
    def check_password(self, given_password: str):
        return bcrypt.checkpw(given_password.encode(), self.password.encode())
    
    def subscribe_to_shows(self, shows: list[str]):
        if len(shows) > 0:
            self.show_subscriptions.extend(shows)
            self.show_subscriptions.sort()
        else:
            raise InvalidSubscriptions('Please provide a list of show subscriptions')

    def subscribe_to_reminders(self, reminders: list[str]):
        if len(reminders) > 0:
            for reminder in reminders:
                if reminder not in self.show_subscriptions:
                    raise InvalidSubscriptions('You have not subscribed to this show. Please subscribe to the show first before subscribing to the reminder')
            self.reminder_subscriptions.extend(reminders)
            self.reminder_subscriptions.sort()
        else:
            raise InvalidSubscriptions('Please provide a list of reminders to subscribe to')
    
    def remove_show_subscriptions(self, shows: list[str]):
        if len(shows) > 0:
            for show in shows:
                try:
                    self.show_subscriptions.remove(show)
                except ValueError:
                    raise InvalidSubscriptions(f'The show {show} does not appear in your show subscriptions')
        else:
            raise InvalidSubscriptions('Please provide a list of shows to unsubscribe from')

    def remove_reminder_subscriptions(self, reminders: list[str]):
        if len(reminders) > 0:
            for reminder in reminders:
                try:
                    self.reminder_subscriptions.remove(reminder)
                except ValueError:
                    raise InvalidSubscriptions(f'The reminder for {reminder} does not appear in your reminder subscriptions')
        else:
            raise InvalidSubscriptions('Please provide a list of reminders to unsubscribe from')
        
    def promote_role(self):
        self.role = 'Admin'
    
    def change_password(self, new_password: str):
        new_hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(14))
        self.password = new_hashed_pw.decode()

    def is_authorised(self, operation: str):
        if self.role == 'Admin':
            return True
        else:
            if 'delete' in operation and 'own-account' not in operation:
                return False
            if 'delete' in operation and 'own-account' in operation:
                return True
            if 'recorded_shows' in operation:
                return False
            return True
    

    def to_dict(self) -> dict[str, str | list[str]]:
        return {
            'username': self.username,
            'show_subscriptions': self.show_subscriptions,
            'reminder_subscriptions': self.reminder_subscriptions,
            'role': self.role
        }