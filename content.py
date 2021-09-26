class BaseContent:
    def __init__(self, name, location, thumbnail, date, id, views, description, public=False):
        self.name = name
        self.location = location
        self.date = date
        self.id = id
        self.public = public
        self.thumbnail = thumbnail
        if self.thumbnail is None or self.thumbnail == "":
            self.thumbnail = "images/NoThumbnail.png"
        self.views = views
        self.description = description
        if self.description is None:
            self.description = ""

    def __repr__(self):
        return self.type() + ": {0} {1} {2}".format(self.name, self.location, self.date)

    def items(self):
        return self.dict().items()

    def dict(self):
        return {'name': self.name, 'location': self.location, 'date': self.date}

    def type(self):
        return "BaseContent"

    def to_list(self):
        return [self.name, self.location, self.thumbnail, self.date, self.views, self.id, self.public == 1]


class Video(BaseContent):
    def type(self):
        return "Video"


class Audio(BaseContent):
    def type(self):
        return "Audio"
