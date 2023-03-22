import csv
import json
import pathlib
from job_info import JobInfo
from site_types import SiteType

base_directory = pathlib.Path(__file__).parents[1]


class JobIntegrator:
    jobs: dict[SiteType, list[JobInfo]] = {}

    def __init__(self) -> None:
        self.jobs = {}

    def add(self, site_type: SiteType, job_list: list) -> None:
        if job_list == {}:
            return

        if self.jobs != {}:
            assert (
                site_type not in self.jobs.keys()
            ), "WARN: site type has exist in jobs dictionary."

        self.jobs[site_type.name] = job_list

    def _groupData(self) -> dict:
        jobs_group = {}

        if not self.jobs:
            return jobs_group

        for platform_name, platform_data in self.jobs.items():
            for item in platform_data:
                platform = {}
                job_unique_key = ""

                job_unique_key = item.title + "_" + item.company
                platform = {
                    "name": platform_name,
                    "updated_time": item.updated_time,
                    "url": item.url,
                }

                if job_unique_key in jobs_group:
                    jobs_group[job_unique_key]["platforms"][platform_name] = platform
                else:
                    platforms = {}
                    job = {}
                    platforms[platform_name] = json.dumps(platform)
                    job = {
                        "title": item.title,
                        "company": item.company,
                        "location": item.location,
                        "platforms": platforms,
                    }
                    jobs_group[job_unique_key] = job

        return jobs_group

    def combineAndExport(self) -> None:
        fields = [
            "title",
            "company",
            "location",
            "platforms",
        ]
        jobs_group = self._groupData()

        with pathlib.Path(base_directory).joinpath("data", "jobs.csv").open(
            "w", encoding="utf-8", newline=""
        ) as f:
            csvfile = csv.DictWriter(f, fieldnames=fields)
            csvfile.writeheader()
            csvfile.writerows(jobs_group.values())


if __name__ == "__main__":
    from jobs_request import RequestHelperHandle

    # for test
    sites = [
        # SiteType.CAKERESUME,
        # SiteType.OZF,
        SiteType.YOURATOR,
    ]

    integrator = JobIntegrator()
    for site_type in sites:
        jobs: list[JobInfo] = []
        request_helper = RequestHelperHandle.get(site_type)
        jobs = request_helper.getJobsList()

        integrator.add(site_type, jobs)

    integrator.combineAndExport()
