import csv
import tempfile
from shutil import which
from pathlib import Path
from utils.cli import *
from job_info import JobInfo
from status_types import StatusType
from site_helper import SiteHelperHandle


OPT_TARGET = "target_file"


@command(
    arg(OPT_TARGET, nargs=1, metavar="TargetJobFile", type=Path,
        help="specify the target file to browse."),
    name="browse", help="browse the job information from the specific file.",
    description="browse the job information from the specific file."
)
def mrwooBrowse(args):
    ARG_TARGET_FILE = Path(getattr(args, OPT_TARGET)[0]).resolve()

    if not ARG_TARGET_FILE.exists():
        print(f"ERROR: file not exist: {ARG_TARGET_FILE}")
        return 1

    if not ARG_TARGET_FILE.is_file():
        print(f"ERROR: target is not file: {ARG_TARGET_FILE}")
        return 1

    if not which("less"):
        print(f"ERROR: 'less' executable not found.")
        return 1

    with tempfile.NamedTemporaryFile("w+", suffix=".tmp.csv", encoding='utf-8', newline='\n') as temp_file:
        temp_reader = csv.writer(temp_file)
        temp_reader.writerow(JobInfo.fieldnames())

        with ARG_TARGET_FILE.open("r", encoding="utf-8") as file:
            job_reader = csv.DictReader(file, fieldnames=JobInfo.fieldnames())
            # skip header
            next(job_reader)

            job_cnt = 0
            while info := JobInfo(next(job_reader, None)):
                job_cnt += 1
                site_helper = SiteHelperHandle.get(info.site)

                try:
                    while True:
                        print(f"{job_cnt}. [{info.status.name}] {info.title} | {info.company} | {info.url}")
                        user_input = input("keep [U]nread / [Y]es to like / [N]o to dislike / [D]etails\n").lower()
                        if user_input == 'u':
                            info.status = StatusType.UNREAD
                            break
                        elif user_input == 'y':
                            info.status = StatusType.LIKE
                            break
                        elif user_input == 'n':
                            info.status = StatusType.DISLIKE
                            break
                        elif user_input == 'd':
                            jd = site_helper.getJobDetails(info)
                            if jd == None:
                                print("no job details available")
                            else:
                                site_helper.browseJobDetails(info, jd)

                    temp_reader.writerow(info)
                except KeyboardInterrupt:
                    print("interrupted by user.")
                    break

            while info := JobInfo(next(job_reader, None)):
                # write remaining job into tempfile.
                temp_reader.writerow(info)

        with ARG_TARGET_FILE.open("w", newline='\n', encoding="utf-8") as file:
            # write back to |ARG_TARGET_FILE|
            temp_file.seek(0)
            while line := temp_file.readline():
                file.write(line)
