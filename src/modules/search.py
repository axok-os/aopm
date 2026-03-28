"""

AOPM search Module
Version: 1.0.0
Made by: GusDev

"""

#libs
import os
from pathlib import Path as p
import aopmAPI as aopm
import json

# api header
header = {
    "name": "search",
    "version": "1.0.0",
    "description": "Search for packages in repositories.",
    "author": "GusDev",
    "author_email": "axok.os.team@gmail.com",
    "api_version": "1.0.0"
}

def get_header() -> dict:
    """
    
    Return the API Header.

    """
    return header

def run(parameters: list, *args) -> int:
    argc = len(parameters)
    argv = parameters

    if argc < 2:
        aopm.error("Too few arguments :(", True)
    
    method = argv[0]
    package_to_search = argv[1]
    repos_index_path = args[2]
    packages_dir = args[4]
    pkg_found_in_repo = None

    aopm.info(f"Searching for: '{package_to_search}'...")

    match method:
        case "repository":
            for repository in p(repos_index_path).iterdir():
                if repository.is_dir():
                    if (repository / "index.json").is_file():
                        repository_content = None
                        with open(str(repository / "index.json"), "r") as f:
                            repository_content = json.load(f)
                        
                        if repository_content:
                            for pkg in repository_content["packages"]:
                                for pkg_name, pkg_data in pkg.items():
                                    if pkg_name == package_to_search:
                                        pkg_found_in_repo = {"aoprepo_path": str(repository / "aoprepo.json"), "index_path": str(repository / "index.json")}
                        else:
                            aopm.error("Cant open: 'index.json' file from repository :(", True)
                    
                    if pkg_found_in_repo:
                        break
            
            if pkg_found_in_repo:
                repo_manifest_content = None
                with open(str(pkg_found_in_repo["aoprepo_path"]), "r") as f:
                    repo_manifest_content = json.load(f)
        
                if repo_manifest_content:
                    aopm.success(f"'{package_to_search}' found in '{repo_manifest_content["name"]}'.")
                    aopm.success("Everything looks done!")
                    return 0
                else:
                    aopm.error("Cant open: 'aoprepo.json' file from repository :(", True)
            else:
                aopm.error(f"Cant found the package: '{package_to_search}' :(", True)

        case "installed":
            for pkg in p(packages_dir).iterdir():
                if pkg.is_dir():
                    if pkg.name == package_to_search:
                        if (pkg / "aopkg.json").is_file():
                            pkg_found_in_repo = True
                        else:
                            aopm.warn("Package directory found. But theres no 'aopkg.json' file.")
                    else:
                        pass
                else:
                    aopm.warn("File found in packages directory.")
            
            if pkg_found_in_repo:
                aopm.success(f"Package: '{package_to_search}' found in 'installed packages'!")
                aopm.success("Everything looks done!")
            else:
                aopm.error(f"Cant found the package: '{package_to_search}' :(", True)



def help():
    title_line = f"{header["name"]}-{header["version"]} Module"
    print(f"""
{title_line}
{"=" * (len(title_line) + 1)}

Description:
-------------
    Search for packages in repositories or installed.

Usage:
    aopm search <tipe> <package>

Examples:
----------
    aopm search repository aopkg    Search for the specified package (aopkg) in the repositories.
    apom search installed aopkg     Search for the specified package (aopkg) in 'installed packages' directory.

Notes:
-------
    You can search only one package.
""")