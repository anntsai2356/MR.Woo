import pathlib
from datetime import datetime
from job_info import JobInfo
from preference_types import PreferenceType
from site_types import SiteType
from utils.file_helper import FileHelper

base_directory = pathlib.Path(__file__).parents[1]


class JobIntegrator:
    fields = [
        "title",
        "company",
        "location",
        "updated_time",
        "url",
        "platform",
        "preference",
    ]
    _jobs = []

    def __init__(self) -> None:
        self._jobs = []

    def add(self, site_type: SiteType, site_jobs: list) -> None:
        if site_jobs == []:
            return

        for site_job in site_jobs:
            item = {}
            item = {
                "title": site_job.title,
                "company": site_job.company,
                "location": site_job.location,
                "updated_time": datetime.fromtimestamp(site_job.updated_time),
                "url": site_job.url,
                "platform": site_type.name,
                "preference": PreferenceType.UNASSIGNED.value,
            }
            self._jobs.append(item)

    def _group(self, data: list) -> dict:
        job_group = {}

        if data == []:
            return job_group

        for job in data:
            platform = {}

            job_unique_key = ""
            job_unique_key = job["title"] + "_" + job["company"]

            # ozf has many url at the same job, so replace it, just save one of them
            platform = {
                "name": job["platform"],
                "updated_time": job["updated_time"],
                "url": job["url"],
            }

            if job_unique_key in job_group:
                job_group[job_unique_key]["platforms"][job["platform"]] = platform
            else:
                platforms = {}
                item = {}
                platforms[job["platform"]] = platform
                item = {
                    "title": job["title"],
                    "company": job["company"],
                    "location": job["location"],
                    "preference": job["preference"],
                    "platforms": platforms,
                }
                job_group[job_unique_key] = item

        return job_group

    def _updateData(self, unique_key, from_data: dict, to_data: dict):
        """
        unique_key: group by title and company for searching
        from_data: fresh data
        to_data: history data

        Update history data with new data.
        """

        platform = {
            "name": from_data["platform"],
            "updated_time": from_data["updated_time"],
            "url": from_data["url"],
        }
        to_data[unique_key]["platforms"][from_data["platform"]] = platform

    def _insertData(self, unique_key, from_data: dict, to_data: dict):
        """
        unique_key: group by title and company for searching
        from_data: fresh data
        to_data: history data

        Insert new data into history data.
        """

        platforms = {}
        job = {}
        platform = {
            "name": from_data["platform"],
            "updated_time": from_data["updated_time"],
            "url": from_data["url"],
        }
        platforms[from_data["platform"]] = platform
        job = {
            "title": from_data["title"],
            "company": from_data["company"],
            "location": from_data["location"],
            "preference": from_data["preference"],
            "platforms": platforms,
        }
        to_data[unique_key] = job

    def _removeGrouping(self, data_group) -> list:
        result = []

        for data in data_group.values():
            for platform_info in data["platforms"].values():
                item = {}
                item = {
                    "title": data["title"],
                    "company": data["company"],
                    "location": data["location"],
                    "updated_time": platform_info["updated_time"],
                    "url": platform_info["url"],
                    "platform": platform_info["name"],
                    "preference": data["preference"],
                }
                result.append(item)

        return result

    def upsert(self, to_file_path) -> None:
        """
        to_file_path: history data file path

        Update exist data and insert new data after comparing fresh data and history data.
        Then the result of upsert will be replaced in self._jobs.
        """

        to_data = FileHelper.importDictData(to_file_path, self.fields)
        if to_data == []:
            return

        to_data_group = self._group(to_data)
        for job in self._jobs:
            unique_key = job["title"] + "_" + job["company"]
            if unique_key in to_data_group.keys():
                self._updateData(unique_key, job, to_data_group)
            else:
                self._insertData(unique_key, job, to_data_group)

        self._jobs = self._removeGrouping(to_data_group)

    def export(self, file_path) -> None:
        FileHelper.exportData(file_path, self.fields, self._jobs, True)


if __name__ == "__main__":
    from jobs_request import RequestHelperHandle

    # for test
    sites = [
        SiteType.CAKERESUME,
        SiteType.OZF,
        SiteType.YOURATOR,
    ]
    file_name = f'jobs_{datetime.now().strftime("%Y-%m-%d")}.csv'
    file_path = pathlib.Path(base_directory).joinpath("data", file_name)
    to_file_path = pathlib.Path(base_directory).joinpath("data", "jobs.csv")
    # ---

    integrator = JobIntegrator()
    for site_type in sites:
        jobs: list[JobInfo] = []
        request_helper = RequestHelperHandle.get(site_type)
        jobs = request_helper.getJobsList()

        integrator.add(site_type, jobs)

    # deal with new result at now
    integrator.export(file_path)

    # deal with new and history result
    integrator.upsert(to_file_path)
    integrator.export(to_file_path)
