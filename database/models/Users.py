import bcrypt


class User:


    def init(self, username: str, password: str, show_subscriptions: list[str], reminder_subscriptions: list[str], role: str):
        self.username = username
        self.password = password
        self.show_subscriptions = show_subscriptions
        self.reminder_subscriptions = reminder_subscriptions
        self.role = role

    @classmethod
    def from_database(cls, user_details: dict[str, str | list[str]]):
        username = user_details['username']
        password = user_details['password']
        show_subscriptions = user_details['show_subscriptions']
        reminder_subscriptions = user_details['reminder_subscriptions']
        role = user_details['role']

        return cls(username, password, show_subscriptions, reminder_subscriptions, role)
    
    @classmethod
    def register_new_user(cls, username: str, password: str, show_subscriptions: list[str], reminder_subscriptions: list[str]):
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(14))

        return cls(username, hashed_password.decode(), show_subscriptions, reminder_subscriptions, 'Standard')
    
    def check_password(self, given_password: str):
        return bcrypt.checkpw(given_password.encode(), self.password.encode())
    
    def subscribe_to_show(self, show: str):
        self.show_subscriptions.append(show)

    def subscribe_to_reminder(self, reminder_show: str):
        self.reminder_subscriptions.append(reminder_show)
    
    def remove_show_subscription(self, show: str):
        self.show_subscriptions.remove(show)

    def remove_reminder_subscription(self, reminder_show: str):
        self.reminder_subscriptions.remove(reminder_show)
    
    def change_password(self, new_password: str):
        new_hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(14))
        self.password = new_hashed_pw.decode()

    def is_authorised(self):
        if self.role == 'Admin':
            return True
        return False
    

    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'show_subscriptions': self.show_subscriptions,
            'reminder_subscriptions': self.reminder_subscriptions,
            'role': self.role
        }