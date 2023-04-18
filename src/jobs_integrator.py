from datetime import datetime
from job_info import JobInfo
from pathlib import Path
from site_types import SiteType
from status_types import StatusType
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
            site = {}

            job_unique_key = ""
            job_unique_key = job["title"] + "_" + job["company"]

            # ozf has many url at the same job, so replace it, just save one of them
            site = {
                "name": job["site"],
                "updated_time": job["updated_time"],
                "url": job["url"],
            }

            if job_unique_key in job_group:
                job_group[job_unique_key]["sites"][job["site"]] = site
            else:
                sites = {}
                item = {}
                sites[job["site"]] = site
                item = {
                    "title": job["title"],
                    "company": job["company"],
                    "location": job["location"],
                    "status": job["status"],
                    "sites": sites,
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

        site = {
            "name": to_data["site"],
            "updated_time": to_data["updated_time"],
            "url": to_data["url"],
        }
        from_data[unique_key]["sites"][to_data["site"]] = site

    def _insertData(self, unique_key, from_data: dict, to_data: dict):
        """
        unique_key: group by title and company for searching
        from_data: history data
        to_data: one of fresh data

        Insert new data into history data.
        """

        sites = {}
        job = {}
        site = {
            "name": to_data["site"],
            "updated_time": to_data["updated_time"],
            "url": to_data["url"],
        }
        sites[to_data["site"]] = site
        job = {
            "title": to_data["title"],
            "company": to_data["company"],
            "location": to_data["location"],
            "status": to_data["status"],
            "sites": sites,
        }
        from_data[unique_key] = job

    def _removeGrouping(self, data_group) -> list:
        result: list[JobInfo] = []

        for data in data_group.values():
            for site_info in data["sites"].values():
                item = JobInfo()
                item.title = data["title"]
                item.company = data["company"]
                item.location = data["location"]
                item.updated_time = site_info["updated_time"]
                item.url = site_info["url"]
                item.site = SiteType(int(site_info["name"]))
                item.status = StatusType(int(data["status"]))

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
        assert to_file.exists(), "to_file_path doesn't exist."

        from_file = Path(from_file_path)
        if not from_file.exists():
            FileHelper.exportData(from_file_path, self.fields, [])
            print(f"The file is not exist. create file ({from_file_path})")

        to_data = FileHelper.importDictData(to_file_path, self.fields)
        assert to_data != [], "nothing to upsert. to_file_path has no any data."

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
    from site_helper import SiteHelperHandle
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
        request_helper = SiteHelperHandle.get(site_type)
        jobs = request_helper.requestJobs(keyword = '後端工程')

        integrator.add(jobs)

    integrator.export(file_path)

    # deal with fresh and history result
    integrator = JobsIntegrator()
    integrator.upsert(history_file_path, file_path)
    integrator.export(history_file_path)

    seconds = time.time() - start_time
    print("Time :", time.strftime("%H:%M:%S", time.gmtime(seconds)))
