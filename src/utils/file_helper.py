import csv


class FileHelper:
    @staticmethod
    def importData(file_path: str, is_skip_header=True) -> list:
        jobs = []

        with open(file_path, "r", encoding="utf-8", newline="") as f:
            file = csv.reader(f)
            if is_skip_header:
                next(file)
            for line in file:
                jobs.append(line)

        return jobs

    @staticmethod
    def importDictData(file_path: str, fields: list, is_skip_header=True) -> list:
        jobs = []

        with open(file_path, "r", encoding="utf-8", newline="") as f:
            file = csv.DictReader(f, fieldnames=fields)
            if is_skip_header:
                next(file)
            jobs = list(file)

        return jobs

    @staticmethod
    def exportData(file_path: str, fields: list, data: list, is_dict_in_list=False):
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            if is_dict_in_list:
                file = csv.DictWriter(f, fieldnames=fields)
                file.writeheader()
            else:
                file = csv.writer(f)
                file.writerow(fields)

            for line in data:
                file.writerow(line)
