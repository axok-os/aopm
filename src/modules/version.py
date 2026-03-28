"""

AOPM version Module
Version: 1.0.0
Made by: GusDev

"""

#libs
import aopmAPI as aopm

# api header
header = {
    "name": "version",
    "version": "1.0.0",
    "description": "See about the AOPM version",
    "author": "GusDev",
    "author_email": "axok.os.team@gmai.com",
    "api_version": "1.0.0"
}

def get_header() -> dict:
    """
    
    Return the API Header.

    """
    return header

def run(parameters: list, *args) -> int:
    api_version = aopm.get_api()
    print(f"""
A     O  P       M          Version: 1.0.0
|     |  |       |          Made by: Axok!_OS Team
Axok!_OS Package Manager    aopmAPI Version: {".".join(map(str, api_version))}
---------------------------------------------------
This program is licensed under the General Public License v2.0 (GPL-2.0)
""")
    return 0

def help():
    title_line = f"{header["name"]}-{header["version"]} Module"
    print(f"""
{title_line}
{"=" * (len(title_line) + 1)}

Description:
-------------
    Display AOPM and aopmAPI informations.

Usage:
-------
    aopm version

Example(s):
----------
    aopm version    Display informations about AOPM and the aopmAPI.
""")