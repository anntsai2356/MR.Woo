from site_types import *
from status_types import *


class JobInfo:
    def __init__(self, csvobj: object = None) -> None:
        self.title: str = ""
        self.company: str = ""
        self.location: str = ""
        self.updated_time: int = 0
        self.url: str = ""
        self.site = SiteType.UNSUPPORTED
        self.status = StatusType.UNREAD

        if csvobj:
            self.title = csvobj["title"]
            self.company = csvobj["company"]
            self.location = csvobj["location"]
            self.updated_time = int(csvobj["updated_time"])
            self.url = csvobj["url"]
            try:
                self.site = SiteType(int(csvobj["site"]))
            except:
                self.site = None
            try:
                self.status = StatusType(int(csvobj["status"]))
            except:
                self.status = None

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

    def __iter__(self):
        return iter(
            [
                self.title,
                self.company,
                self.location,
                self.updated_time,
                self.url,
                self.site.value,
                self.status.value,
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
        if not isinstance(self.site, SiteType):
            return False
        if not isinstance(self.status, StatusType):
            return False
        return True
