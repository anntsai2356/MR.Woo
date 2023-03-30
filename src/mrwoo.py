import sys
import argparse
from pathlib import Path
from jobs_request import RequestHelperHandle
from jobs_integrator import JobsIntegrator
from pathlib import Path
from site_types import SiteType
from datetime import datetime


PROG_NAME = "mrwoo"

DEFAULT_OUTPUT = Path(__file__).parent.joinpath(
    "..", "data", f'jobs_{datetime.now().strftime("%Y-%m-%d")}.csv').resolve()
DEFAULT_SITES = set(filter(lambda t: t != SiteType.UNSUPPORTED, SiteType))
OPT_DEST = "out_dest"
OPT_KEYWORD = "keyword"
OPT_SITES = "opt_sites"


OPT_FROM_SITES = set([])


def toSite(string: str):
    OPT_FROM_SITES.add(SiteType.cast(string))
    return string


def parseArgs():
    parser = argparse.ArgumentParser(PROG_NAME, description="\n".join([
        f"{PROG_NAME} is a command line program to request and integrate jobs "
        "details from some job site."
    ]))

    # positional args
    parser.add_argument(OPT_KEYWORD, nargs="+", metavar="SearchKeyword",
                        help="specify the keyword for searching. [WIP]")

    parser.add_argument("-C", dest=OPT_DEST, action="store", type=Path,
                        default=str(DEFAULT_OUTPUT), metavar="OutputPath",
                        help="specify the destination to output the jobs information.")

    parser.add_argument("-s", dest=OPT_SITES, type=toSite,
                        default=None, choices=SiteType.getStrList(),
                        help="specify the site to query.")

    return parser.parse_args()


def mrwooMain():
    args = parseArgs()
    ARG_KEYWORD = getattr(args, OPT_KEYWORD)
    ARG_DEST = Path(getattr(args, OPT_DEST))
    ARG_SITES = OPT_FROM_SITES or DEFAULT_SITES

    if SiteType.UNSUPPORTED in ARG_SITES:
        print("ERROR: invalid type.")
        return 1

    integrator = JobsIntegrator()
    for site in ARG_SITES:
        print(f"requesting with keyword {ARG_KEYWORD} in |{site.name}|.")
        request_helper = RequestHelperHandle.get(site)
        integrator.add(request_helper.getJobsList())

    if not ARG_DEST.parent.exists():
        ARG_DEST.parent.mkdir(exist_ok=True)

    integrator.export(ARG_DEST)
    return 0


try:
    sys.exit(mrwooMain())

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
