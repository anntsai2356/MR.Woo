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

    def groupData(self) -> dict:
        jobs = {}

        job_sites_data = {}
        for jos_site_name in self.job_sites:
            job_sites_data[jos_site_name] = self.importData(jos_site_name)

        for platform_name, platform_data in job_sites_data.items():
            for item in platform_data:
                platform = {}
                job_unique_key = ""

                job_unique_key = item["title"] + "_" + item["company"]
                platform = {
                    "name": platform_name,
                    "updated_time": item["updated_time"],
                    "url": item["url"],
                }

                if job_unique_key in jobs:
                    jobs[job_unique_key]["platforms"][platform_name] = platform
                else:
                    platforms = {}
                    job = {}
                    platforms[platform_name] = platform
                    job = {
                        "title": item["title"],
                        "company": item["company"],
                        "location": item["location"],
                        "platforms": platforms,
                    }
                    jobs[job_unique_key] = job

        return jobs

    def build(self):
        fields = [
            "title",
            "company",
            "location",
            "platforms",
        ]
        jobs = self.groupData()

        with pathlib.Path(base_directory).joinpath("data", "jobs.csv").open(
            "w", encoding="utf-8", newline=""
        ) as f:
            csvfile = csv.DictWriter(f, fieldnames=fields)
            csvfile.writeheader()
            for job in jobs.values():
                platforms_join = "|"
                for item in job["platforms"].values():
                    item_string = "/".join(
                        f"{key}:{value}" for key, value in item.items()
                    )
                    platforms_join += item_string + "|"

                job["platforms"] = platforms_join
                csvfile.writerow(job)


if __name__ == "__main__":
    j = JobIntegrater()
    jobs = j.build()

    # import json

    # jobs_json = json.dumps(jobs, ensure_ascii=False)
    # print(jobs_json)
