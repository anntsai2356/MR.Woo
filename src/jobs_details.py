class JobDetail:
    def __init__(self) -> None:
        self.title: str = ""
        self.detail: str = ""
        self.company: str = ""
        self.location: str = ""
        self.created_time: int = 0
        self.updated_time: int = 0
        self.salary_min: int = 0
        self.salary_max: int = 0
        self.url: str = ""