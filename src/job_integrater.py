import csv
import pathlib
from job_info import JobInfo

base_directory = pathlib.Path(__file__).parents[1]


class JobIntegrater:
    job_sites = [
        "cakeresume",
        "ozf",
        "yourator",
    ]

    def __init__(self) -> None:
        pass

    def importData(self, job_site) -> list:
        jobs = []

        with pathlib.Path(base_directory).joinpath("temp", job_site + ".csv").open(
            "r", encoding="utf-8", newline=""
        ) as f:
            csvfile = csv.DictReader(f, fieldnames=JobInfo.fieldnames())
            next(csvfile)  # skip header
            for line in csvfile:
                jobs.append(line)

        return jobs


if __name__ == "__main__":
    j = JobIntegrater()
    jobs = j.importData("yourator")

    import json

    jobs_json = json.dumps(jobs, ensure_ascii=False)
    print(jobs_json)
