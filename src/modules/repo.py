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
import requests
import sys
from tqdm import tqdm
import shutil


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
def run(parameters: list, *args) -> int:
    # simplify the parameters
    argc = len(parameters)
    argv = parameters

    if argc < 1:
        aopm.error("Too few arguments :(", True)
    
    match argv[0]:
        case "create":
            if argc < 2:
                aopm.error("No repository name to create specified :(", True)
            
            repo_name = argv[1]
            repo_dir = args[1]
            repo_link = ""
            repo_download_link = ""

            aopm.info(f"Creating repository named: '{repo_name}'...")

            # get the repo link
            while repo_link == "":
                user_repo_link = input("Repository link(not the download link): ")
                if user_repo_link.strip().lower() == "":
                    aopm.error("The repository link cannot be empty. Try again :)")
                    continue
                else:
                    try:
                        r = requests.get(user_repo_link, timeout=5)

                        match r.status_code:
                            case 200:
                                aopm.success("The website exists!")
                                repo_link = user_repo_link
                            case 404:
                                aopm.error("The website dont exist :(")
                                continue
                    except requests.exceptions.RequestException:
                        aopm.error("The website dont exist, or cant connect :(")
                        continue
                    except requests.exceptions.Timeout:
                        aopm.error("Connection timed out :(")
                        continue

            # get the repo download link
            while repo_download_link == "":
                user_download_link = input("Repository download link: ")
                if user_download_link.strip().lower() == "":
                    aopm.error("The repository download link cannot be empty. Try again :)")
                    continue
                else:
                    try:
                        r = requests.get(user_download_link, timeout=5)

                        match r.status_code:
                            case 200:
                                aopm.success("The download link exists!")
                                repo_download_link = user_download_link
                            case 404:
                                aopm.error("The download link dont exist :(")
                                continue
                    except requests.exceptions.RequestException:
                        aopm.error("The download link dont exist, or cannot connect :(")
                        continue
                    except requests.exceptions.Timeout:
                        aopm.error("Connection timed out :(")
                        continue

            # check if the link is the same as the download link
            if user_repo_link == user_download_link:
                aopm.warn("The repository link and the download link are the same!")
            
            # gen the manifes.json
            repo_manifest = {
                "name" : repo_name,
                "link": repo_link,
                "download_link": repo_download_link,
                "type": "user-added",
                "repo_type": "sourceforge"
            }
            # create the repo folder
            os.makedirs(f"{repo_dir}/{repo_name}", exist_ok=True)
            # open and write the repo
            with open(f"{repo_dir}/{repo_name}/aoprepo.json", "w") as f:
                json.dump(repo_manifest, f)

            aopm.success(f"Repository added successfully! To use the repository use: 'aopm repo init {repo_name}'")
            aopm.info("The repository type is sourceforge. If you want another type edit the repo.json file")
            return 0
        case "init":
            if argc < 2:
                aopm.error("No repository to init specified :(", True)
            
            repo_to_init = argv[1]
            repo_dir = args[1]
            repo_index_dir = args[2]
            
            if p(f"{repo_dir}/{repo_to_init}").is_dir():
                pass
            else:
                aopm.error(f"No repository named: '{repo_to_init}' found to init :(", True)
            
            try:
                with open(f"{repo_dir}/{repo_to_init}/aoprepo.json", "r") as f:
                    repo_index = json.load(f)
            
            except json.JSONDecodeError:
                aopm.error("The repository manifest probably is corrupted :(", True)
            
            
            if "download_link" in repo_index:
                if "repo_type" in repo_index:
                    pass
                else:
                    aopm.error("The variable 'repo_type' dont exist in the repository index :(", True)
            else:
                aopm.error("The variable 'download_link' dont exist in the repository index :(", True)
            
            try:
                os.makedirs(f"{repo_index_dir}/{repo_index["name"]}")
            except FileExistsError:
                aopm.warn(f"Already exist a directory named: '{repo_index["name"]}'. If you want to delete use: 'aopm repo deinit {repo_index["name"]}'")
                return 1
            match repo_index["repo_type"]:
                case "sourceforge":
                    r = requests.get(f"{repo_index["download_link"]}/index.json/download", stream=True)
                    total = int(r.headers.get("content-length", 0))
                    
                    try:
                        with open(f"{repo_index_dir}/{repo_index["name"]}/index.json", "wb") as f:
                            with tqdm(total=total, unit="B", unit_scale=True, unit_divisor=1024, desc="Downloading index.json") as bar:
                                for chunk in r.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        bar.update(len(chunk))
                    except FileExistsError:
                        aopm.warn(f"Already exist a index.json. If you want delete use: 'aopm repo deinit {repo_index["name"]}'")
                        return 1
                case "github":
                    r = requests.get(f"{repo_index["download_link"]}/index.json", stream=True)
                    total = int(r.headers.get("content-length", 0))
                    
                    try:
                        with open(f"{repo_index_dir}/{repo_index["name"]}/index.json", "wb") as f:
                            with tqdm(total=total, unit="B", unit_scale=True, unit_divisor=1024, desc="Downloading index.json") as bar:
                                for chunk in r.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        bar.update(len(chunk))
                    except FileExistsError:
                        aopm.warn(f"Already exist a index.json. If you want delete use: 'aopm repo deinit {repo_index["name"]}'")
                        return 1
                case "direct":
                    r = requests.get(f"{repo_index["download_link"]}/index.json", stream=True)
                    total = int(r.headers.get("content-length", 0))
                    
                    try:
                        with open(f"{repo_index_dir}/{repo_index["name"]}/index.json", "wb") as f:
                            with tqdm(total=total, unit="B", unit_scale=True, unit_divisor=1024, desc="Downloading index.json") as bar:
                                for chunk in r.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        bar.update(len(chunk))
                    except FileExistsError:
                        aopm.warn(f"Already exist a index.json. If you want delete use: 'aopm repo deinit {repo_index["name"]}'")
                        return 1
                case _:
                    aopm.error(f"Invalid variable: 'repo_type': '{repo_index["repo_type"]}' :(", True)
            
            try:
                if p(f"{repo_dir}/{repo_to_init}/aoprepo.json").is_file():
                    shutil.copy(f"{repo_dir}/{repo_to_init}/aoprepo.json", f"{repo_index_dir}/{repo_to_init}/aoprepo.json")
            except FileExistsError:
                aopm.warn(f"Already exist a aoprepo.json. If you want delete use: 'aopm repo deinit {repo_index["name"]}'")

        case "shutdown":
            if argc < 2:
                aopm.error("No repository name to shutdown specified :(", True)
            
            repo_to_deinit = argv[1]
            repos_index_dir = args[2]

            try:
                shutil.rmtree(f"{repos_index_dir}/{repo_to_deinit}")
            except FileNotFoundError:
                aopm.info(f"Dont exist a repository named: '{repo_to_deinit}' :/")
                return 0
            

        case "list":
            if argc < 2:
                aopm.error("No repository type to show specified :(", True)
            
            repo_type_to_show = argv[1]
            repos_index_dir = args[2]
            repos_dir = args[1]

            repos_found_in_active_folder = []
            repos_found_in_deactive_folder = []

            # active
            for repo_dir in p(repos_index_dir).iterdir():
                if repo_dir.is_dir():
                    repos_found_in_active_folder.append(repo_dir)
                else:
                    aopm.warn(f"File: '{repo_dir}' found in repositoires directory.")
            
            # deactive
            for repo_dir in p(repos_dir).iterdir():
                if repo_dir.is_dir():
                    repos_found_in_deactive_folder.append(repo_dir)
                else:
                    aopm.warn(f"File: '{repo_dir}' found in repositories directory.")
            
            match repo_type_to_show:
                case "active":
                    print("active repositories found:".title())
                    for i, repository in enumerate(repos_found_in_active_folder):
                        preffix = "└──" if i == len(repos_found_in_active_folder) - 1 else "├──"
                        print(f"{preffix} {repository.name}")

                    print("-" * 30)
                    return 0
                case "deactive":
                    print("deactive repositories found:".title())
                    active_names = {repo.name for repo in repos_found_in_active_folder}
                    deactive = [
                        repo for repo in repos_found_in_deactive_folder
                        if repo.name not in active_names
                    ]

                    for i, repository in enumerate(deactive):
                        preffix = "└──" if i == len(deactive) - 1 else "├──"
                        print(f"{preffix} {repository.name}")
                    
                    print("-" * 30)
                case _:
                    aopm.error(f"Invalid repository type specified: '{repo_type_to_show}'")
        case "remove":
            pass
        
        case _:
            aopm.error("Invalid operation specified :(", True)


# display your custom help message
def help():
    title_line = f"{header["name"]}-{header["version"]} Module"
    print(f"""
{title_line}
{"=" * (len(title_line + 1))}

Description:
-------------
    Create, remove, init, shutdown and show repositories.

Usage:
    aopm repo <operation> <repository>

Example(s):
----------
    aopm repo create core      Create a repository with the specified name.
    aopm repo init core        Init the specified repository name.
    aopm repo show active      Show all activated repostiories found.
    aopm repo show deactive    Show all deactivated repositories found.
    aopm repo shutdown core    Shutdown the specified repository name.
""")
