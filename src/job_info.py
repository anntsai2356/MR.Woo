import time

class JobInfo:
    def __init__(self) -> None:
        self.title: str = ""
        self.company: str = ""
        self.location: str = ""
        self.created_time: int = 0
        self.updated_time: int = 0
        self.url: str = ""

    def __bool__(self):
        if not isinstance(self.title, str) or self.title == "":
            return False
        if not isinstance(self.company, str) or self.company == "":
            return False
        if not isinstance(self.location, str) or self.location == "":
            return False
        if not isinstance(self.created_time, int):
            return False
        if not isinstance(self.updated_time, int):
            return False
        if not isinstance(self.url, str) or self.url == "":
            return False
        return True

    def __str__(self):
        return '\n'.join([
            f'title       : {self.title}',
            f'company     : {self.company}',
            f'location    : {self.location}',
            f'created_time: {self.created_time} -> {time.strftime("%Y-%m-%dT%H:%m%S", time.localtime(self.created_time))}',
            f'updated_time: {self.updated_time} -> {time.strftime("%Y-%m-%dT%H:%m%S", time.localtime(self.updated_time))}',
            f'url         : {self.url}',
        ])