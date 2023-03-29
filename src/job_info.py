from preference_types import *


class JobInfo:
    def __init__(self, csvobj: object = None) -> None:
        self.title: str = ""
        self.company: str = ""
        self.location: str = ""
        self.updated_time: int = 0
        self.url: str = ""
        self.platform: str = ""
        self.preference: int = PreferenceType.UNASSIGNED

        if csvobj:
            self.title = csvobj["title"]
            self.company = csvobj["company"]
            self.location = csvobj["location"]
            self.updated_time = int(csvobj["updated_time"])
            self.url = csvobj["url"]
            self.platform = csvobj["platform"]
            self.preference = csvobj["preference"]

    @staticmethod
    def fieldnames():
        return ["title", "company", "location", "updated_time", "url", "platform", "preference"]

    def toBuiltinDict(self):
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "updated_time": self.updated_time,
            "url": self.url,
            "platform": self.platform,
            "preference": self.preference,
        }

    def __bool__(self):
        if not isinstance(self.title, str) or self.title == "":
            return False
        if not isinstance(self.company, str) or self.company == "":
            return False
        if not isinstance(self.location, str):
            return False
        if not isinstance(self.updated_time, int):
            return False
        if not isinstance(self.url, str) or self.url == "":
            return False
        if not isinstance(self.platform, str) or self.platform == "":
            return False
        if not isinstance(self.preference, int):
            return False
        return True
