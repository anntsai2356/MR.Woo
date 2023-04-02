from pathlib import Path
from site_helper import SiteHelperHandle
from jobs_integrator import JobsIntegrator
from site_types import SiteType
from datetime import datetime
from utils.cli import *


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


@command(
    arg(OPT_KEYWORD, metavar="SearchKeyword",
        help="specify the keyword for searching. [WIP]"),
    arg("-C", dest=OPT_DEST, action="store", type=Path, default=str(DEFAULT_OUTPUT),
        metavar="OutputPath",
        help="specify the destination to output the jobs information."),
    arg("-s", dest=OPT_SITES, type=toSite, default=None,
        choices=SiteType.getStrList(),
        help="specify the site to query."),
    name="fetch", help="fetch the job information from certain sites.",
    description="fetch the job information from certain sites."
)
def mrwooFetch(args):
    ARG_KEYWORD = getattr(args, OPT_KEYWORD)
    ARG_DEST = Path(getattr(args, OPT_DEST))
    ARG_SITES = OPT_FROM_SITES or DEFAULT_SITES

    if SiteType.UNSUPPORTED in ARG_SITES:
        print("ERROR: invalid type.")
        return 1

    integrator = JobsIntegrator()
    for site in ARG_SITES:
        print(f"requesting with keyword {ARG_KEYWORD} in |{site.name}|.")
        site_helper = SiteHelperHandle.get(site)
        integrator.add(site_helper.requestJobs(keyword = ARG_KEYWORD))

    if not ARG_DEST.parent.exists():
        ARG_DEST.parent.mkdir(exist_ok=True)

    integrator.export(ARG_DEST)
    return 0
