from status_types import *


class JobInfo:
    def __init__(self, csvobj: object = None) -> None:
        self.title: str = ""
        self.company: str = ""
        self.location: str = ""
        self.updated_time: int = 0
        self.url: str = ""
        self.site: str = ""
        self.status: int = StatusType.UNREAD.value

        if csvobj:
            self.title = csvobj["title"]
            self.company = csvobj["company"]
            self.location = csvobj["location"]
            self.updated_time = int(csvobj["updated_time"])
            self.url = csvobj["url"]
            self.site = csvobj["site"]
            self.status = csvobj["status"]

    @staticmethod
    def fieldnames():
        return [
            "title",
            "company",
            "location",
            "updated_time",
            "url",
            "site",
            "status",
        ]

    def toBuiltinDict(self):
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "updated_time": self.updated_time,
            "url": self.url,
            "site": self.site,
            "status": self.status,
        }

    def __iter__(self):
        return iter(
            [
                self.title,
                self.company,
                self.company,
                self.updated_time,
                self.url,
                self.site,
                self.status,
            ]
        )

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
        if not isinstance(self.site, str) or self.site == "":
            return False
        if not isinstance(self.status, int):
            return False
        return True
