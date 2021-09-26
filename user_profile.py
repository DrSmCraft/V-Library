import uuid

class UserProfile:
    def __init__(self, username, email, first_name, last_name, avatar, public, id, can_publish):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.avatar = avatar
        if self.avatar is None or self.avatar == "":
            self.avatar = "images/User.png"
        self.public = public
        self.id = id
        self.can_publish = int(can_publish) > 0

    def __repr__(self):
        return "User: {0} {1} has username of {2} and email of {3}".format(self.first_name, self.last_name,
                                                                           self.username, self.email)

    def items(self):
        return self.dict().items()

    def dict(self):
        return {'Username': self.username, 'Email': self.email, 'FirstName': self.first_name,
                'LastName': self.last_name, 'Avatar': self.avatar, 'Public': self.public, 'Id': self.id}

    def json(self):
        return '{"username":"%s", "email":"%s", "first_name":"%s", "last_name":"%s", "avatar":"%s","public":"%s","id":"%s", "can_publish":%s}' % (
        self.username, self.email, self.first_name, self.last_name, self.avatar, self.public, self.id, str(self.can_publish).lower())


def generate_new_user_id():
    return uuid.uuid1().hex