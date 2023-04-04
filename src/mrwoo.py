import sys
import dcli


@dcli.command(
    "mr-woo",
    description="mrwoo is a command line tool to browse jobs in the terminal."
)
def mrwooMain():
    return 0


# import sub commands
from mrwoo_fetch import *
from mrwoo_browse import *


mrwooMain.addSubCommand(mrwooFetch)
mrwooMain.addSubCommand(mrwooBrowse)


try:
    sys.exit(mrwooMain())

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
