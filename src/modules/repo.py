"""

AOPM repo Module
Version: 1.0.0
Made by: GusDev

"""

# libs:
# ------
#   All the libs that the module will use

import json
import aopmAPI as aopm
import os
from pathlib import Path as p


# The API Header
header = {
    "name": "repo",
    "version": "1.0.0",
    "description": "Manage repositories.",
    "author": "GusDev",
    "author_email": "axok.os.team@gmail.com",
    "api_version": "1.0.0"
}

# return the API Header
def get_header() -> dict:
    return header

# the core will run this
def run(parameters: list, *args):
    pass

# display your custom help message
def help():
    pass
