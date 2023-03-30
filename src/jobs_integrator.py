from pathlib import Path
from datetime import datetime
from job_info import JobInfo
from utils.file_helper import FileHelper

base_directory = Path(__file__).parents[1]


class JobsIntegrator:
    def __init__(self) -> None:
        self.fields = JobInfo.fieldnames()
        self._jobs: list[JobInfo] = []

    def add(self, site_jobs: list) -> None:
        if site_jobs == []:
            return

        for site_job in site_jobs:
            self._jobs.append(site_job)

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
                    "status": job["status"],
                    "platforms": platforms,
                }
                job_group[job_unique_key] = item

        return job_group

    def _updateData(self, unique_key, from_data: dict, to_data: dict):
        """
        unique_key: group by title and company for searching
        from_data: history data
        to_data: one of fresh data

        Update history data with new data.
        """

        platform = {
            "name": to_data["platform"],
            "updated_time": to_data["updated_time"],
            "url": to_data["url"],
        }
        from_data[unique_key]["platforms"][to_data["platform"]] = platform

    def _insertData(self, unique_key, from_data: dict, to_data: dict):
        """
        unique_key: group by title and company for searching
        from_data: history data
        to_data: one of fresh data

        Insert new data into history data.
        """

        platforms = {}
        job = {}
        platform = {
            "name": to_data["platform"],
            "updated_time": to_data["updated_time"],
            "url": to_data["url"],
        }
        platforms[to_data["platform"]] = platform
        job = {
            "title": to_data["title"],
            "company": to_data["company"],
            "location": to_data["location"],
            "status": to_data["status"],
            "platforms": platforms,
        }
        from_data[unique_key] = job

    def _removeGrouping(self, data_group) -> list:
        result: list[JobInfo] = []

        for data in data_group.values():
            for platform_info in data["platforms"].values():
                item = JobInfo()
                item.title = data["title"]
                item.company = data["company"]
                item.location = data["location"]
                item.updated_time = platform_info["updated_time"]
                item.url = platform_info["url"]
                item.platform = platform_info["name"]
                item.status = data["status"]

                result.append(item)

        return result

    def upsert(self, from_file_path, to_file_path) -> None:
        """
        from_file_path: history data file path
        to_file_path: fresh data file path

        Update exist data and insert new data after comparing fresh data and history data.

        important! >> The result of upsert will be replaced in self._jobs.
        """

        to_file = Path(to_file_path)
        assert to_file.exists(), "WARN: to_file_path doesn't exist."

        from_file = Path(from_file_path)
        if not from_file.exists():
            FileHelper.create(from_file_path)
            FileHelper.exportData(from_file_path, self.fields, [])
            print(f"The file is not exist. create file ({from_file_path})")

        to_data = FileHelper.importDictData(to_file_path, self.fields)
        assert to_data != [], "WARN: Nothing to upsert. to_file_path has no any data."

        from_data = FileHelper.importDictData(from_file_path, self.fields)

        from_data_group = self._group(from_data)
        for job in to_data:
            unique_key = job["title"] + "_" + job["company"]
            if unique_key in from_data_group.keys():
                self._updateData(unique_key, from_data_group, job)
            else:
                self._insertData(unique_key, from_data_group, job)

        self._jobs = self._removeGrouping(from_data_group)

    def export(self, file_path) -> None:
        FileHelper.exportData(file_path, self.fields, self._jobs)


if __name__ == "__main__":
    from jobs_request import RequestHelperHandle
    from site_types import SiteType
    import time

    start_time = time.time()

    # for test
    sites = [
        SiteType.CAKERESUME,
        SiteType.OZF,
        SiteType.YOURATOR,
    ]
    file_name = f'jobs_{datetime.now().strftime("%Y-%m-%d")}.csv'
    file_path = Path(base_directory).joinpath("data", file_name)
    history_file_path = Path(base_directory).joinpath("data", "jobs.csv")
    # ---

    # deal with fresh result
    integrator = JobsIntegrator()
    for site_type in sites:
        jobs: list[JobInfo] = []
        request_helper = RequestHelperHandle.get(site_type)
        jobs = request_helper.getJobsList()

        integrator.add(jobs)

    integrator.export(file_path)

    # deal with fresh and history result
    integrator = JobsIntegrator()
    integrator.upsert(history_file_path, file_path)
    integrator.export(history_file_path)

    seconds = time.time() - start_time
    print("Time :", time.strftime("%H:%M:%S", time.gmtime(seconds)))
