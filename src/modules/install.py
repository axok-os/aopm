"""

AOPM install Module
Version: 1.0.0
Made by: GusDev

"""

#libs

import subprocess as sub
from pathlib import Path as p
from tqdm import tqdm
import aopmAPI as aopm
import json
import requests
import tempfile
import tarfile
import os
import hashlib
import shutil

# api header
header = {
    "name": "install",
    "version": "1.0.0",
    "description": "Install packages.",
    "author": "gusdev",
    "author_email": "axok.os.team@gmail.com",
    "api_version": "1.0.0"
}

def get_header() -> dict:
    """
    
    Return the API header.
    
    """
    return header

def get_sha(pkg):
    sha256 = hashlib.sha256()

    with open(pkg, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
        
    return sha256.hexdigest()

def run(parameters: list, *args) -> int:
    argv = parameters
    argc = len(parameters)

    if argc < 1:
        aopm.error("Too few arguments :(", True)
    
    package_to_search = argv[0]
    repos_index_path = args[2]
    pkg_found_in_repo = None

    aopm.info("Searching for the package...")

    for repository in p(repos_index_path).iterdir():
        if repository.is_dir():
            if (repository / "index.json").is_file():
                repository_content = None
                with open (str(repository / "index.json"), "r") as f:
                    repository_content = json.load(f)
                
                if repository_content:
                    for pkg in repository_content["packages"]:
                        for pkg_name, pkg_data in pkg.items():
                            if pkg_name == package_to_search:
                                pkg_found_in_repo = {"aoprepo_path": str(repository / "aoprepo.json"), "index_path": str(repository / "index.json")}
                else:
                    aopm.error("Cant open index.json from repository :(", True)
        else:
            aopm.warn("File found in repositories directory.")
        
        if pkg_found_in_repo:
            break
    
    if pkg_found_in_repo:
        aopm.success("Package found!")
    else:
        aopm.error(f"Cant found the package: '{package_to_search}' :(", True)
    
    try:
        repository_manifest_content = json.load(open(pkg_found_in_repo["aoprepo_path"], "r"))
    except FileNotFoundError:
        aopm.error("Cant found repository manifest :(", True)
    
    try:
        repository_index_content = json.load(open(pkg_found_in_repo["index_path"], "r"))
    except FileNotFoundError:
        aopm.error("Cant found repository index :(", True)
    
    aopm.info("Creating chace directory...")
    with tempfile.TemporaryDirectory() as tmp:
        aopm.success("Cache directory created!")

        match repository_manifest_content["repo_type"]:
            case "sourceforge":
                r = requests.get(f"{repository_manifest_content["download_link"]}/packages/{package_to_search}.aopkg.tar.xz/download", stream=True)
                total = int(r.headers.get("content-length", 0))

                aopm.info("Downloading package...")
                with open(f"{tmp}/{package_to_search}.aopkg.tar.xz", "wb") as f, tqdm(
                    desc="Downloading package...",
                    unit='B',
                    unit_divisor=1024,
                    unit_scale=True,
                    total=total,
                    ascii=" #",
                    bar_format="{desc} [{bar}] {percentage:3.0f}%"
                ) as bar:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            size = f.write(chunk)
                            bar.update(size)

                aopm.success("Package downloaded!")
            case "github":
                r = requests.get(f"{repository_manifest_content["download_link"]}/packages/{package_to_search}.aopkg.tar.xz", stream=True)
                total = int(r.headers.get("content-length", 0))

                aopm.info("Downloading package...")
                with open(f"{tmp}/{package_to_search}.aopkg.tar.xz", "wb") as f, tqdm(
                    desc="Downloading package...",
                    unit='B',
                    unit_divisor=1024,
                    unit_scale=True,
                    ascii=" #",
                    total=total,
                    bar_format="{desc} [{bar}] {percentage:3.0f}%"
                ) as bar:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            size = f.write(chunk)
                            bar.update(chunk)
                aopm.success("Package downloaded!")
            case "direct":
                r = requests.get(f"{repository_manifest_content["download_link"]}/packages/{package_to_search}.aopkg.tar.xz", stream=True)
                total = int(r.headers.get("content-length", 0))

                aopm.info("Downloading package...")
                with open(f"{tmp}/{package_to_search}.aopkg.tar.xz", "wb") as f, tqdm(
                    desc="Downloading package...",
                    unit='B',
                    unit_divisor=1024,
                    unit_scale=True,
                    ascii=" #",
                    total=total,
                    bar_format="{desc} [{bar}] {percentage:3.0f}%"
                ) as bar:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            size = f.write(chunk)
                            bar.update(chunk)
                aopm.success("Package downloaded!")
        
        aopm.info("Creating main directories")
        main_dirs = [
            f"{tmp}/extract1",
            f"{tmp}/extract2"
        ]
        for dirs in main_dirs:
            os.makedirs(dirs, exist_ok=True)
        
        aopm.success("Main directories created!")
        aopm.info("Making first extract...")

        with tarfile.open(f"{tmp}/{package_to_search}.aopkg.tar.xz", "r:xz") as tar:
            tar.extractall(f"{tmp}/extract1")

        aopm.success("First extract done!")
        
        aopm.info("Checking if the SHA256 match...")
        sha_to_match = None
        try:
            with open(f"{tmp}/extract1/sha256", "r") as f:
                sha_to_match = f.read()
        except FileNotFoundError:
            aopm.error("Cant found the sha256 file from package :(", True)

        if sha_to_match:
            if get_sha(f"{tmp}/extract1/{package_to_search}.tar.xz") == sha_to_match:
                aopm.success("The SHA256 match!")
            else:
                aopm.error("The SHA256 from package dont match :(. For security reasons, we will not install.\nIf you want install anyway edit the '/etc/aopm.d/aopm.conf'", True)
        
        aopm.info("Checking if package have GPG signature...")
        verified = False
        if p(f"{tmp}/extract1/{package_to_search}.tar.xz.sig").is_file():
            aopm.info("GPG signature found! Checking...")
            keys_path = args[3]
            for key_file in p(f"{keys_path}").iterdir():
                if key_file.is_dir():
                    if (key_file / "key.asc").is_file():
                        gpg = aopm.GPG_mantainer(tmp)
                        gpg.import_key(str(p(key_file / "key.asc")))
                        verified = gpg.verify_file(f"{tmp}/extract1/{package_to_search}.tar.xz.sig", f"{tmp}/extract1/{package_to_search}.tar.xz")
                    else:
                        aopm.warn("Empty directory in keys directory.")
                else:
                    aopm.warn("File found in keys directory.")

                if verified:
                    break
            if verified:
                aopm.success("GPG signature verified!")
            else:
                aopm.error("GPG signature verification failed :(")
        else:
            aopm.info("No GPG signature found.")
        
        aopm.info("Making second extract...")

        with tarfile.open(f"{tmp}/extract1/{package_to_search}.tar.xz", "r:xz") as tar:
            tar.extractall(f"{tmp}/extract2")
        
        aopm.success("Second extract done!")

        aopm.info("Checking some files...")
        must_dirs = [
            f"{tmp}/extract2/aopkg-tools",
            f"{tmp}/extract2/files"
        ]

        must_files = [
            f"{tmp}/extract2/aopkg-tools/install.sh",
            f"{tmp}/extract2/file-list",
            f"{tmp}/extract2/aopkg.json"
        ]

        for dirs in must_dirs:
            if p(dirs).is_dir():
                pass
            else:
                aopm.error(f"Cant found the directory: '{dirs}' in package :(", True)
        
        for files in must_files:
            if p(files).is_file():
                pass
            else:
                aopm.error(f"Cant found the file: '{files}' in package :(", True)
        
        aopm.info("Opening manifest...")
        aopkg_manifest_content = json.load(open(f"{tmp}/extract2/aopkg.json", "r"))
        print("\n")
        print("package detected!".title())
        print("-" * 30)
        if verified:
            pass
        else:
            print("The package GPG signature verification failed.\nInstall at your own risk. This package may be unsafe or tampered.")
            print("-" * 30)
        for key in aopkg_manifest_content:
            print(f"{str(key).title().replace("_", " ").replace("-", " ")}: {(aopkg_manifest_content[key])}")
        print("-" * 30)

        # get confirm
        if "--force" in argv:
            user_confirm = True
        else:
            user_confirm = None
            while user_confirm == None:
                user_input = input("Want install this package?[y/N]: ").strip()
                if user_input.lower() == "":
                    aopm.warn("No option found. Using preset: 'False'...")
                    user_confirm = False
                else:
                    match user_input.lower():
                        case "y"|"yes":
                            user_confirm = True
                        case "n"|"no":
                            user_confirm = False
                        case _:
                            aopm.error("Invalid option specified :(. Try again")
                            continue
        
        if user_confirm:
            if verified:
                pass
            else:
                print("The package GPG signature verification failed.\nInstall at your own risk. This package may be unsafe or tampered.")
                user_confirm_warn = None
                if "--no-warn" in argv:
                    user_confirm_warn = True
                else:
                    while user_confirm_warn == None:
                        user_input = input(f"Want install the package: '{package_to_search}'?[y/N]: ").strip().lower()
                        if user_input == "":
                            aopm.warn("No option found. Using preset: 'False'...")
                            user_confirm_warn = False
                        else:
                            match user_input:
                                case "y"|"yes":
                                    user_confirm_warn = True
                                case "n"|"no":
                                    user_confirm_warn = False
                                case _:
                                    aopm.error("Invalid option specified :(. Try again.")
                                    continue
                    match user_confirm_warn:
                        case True:
                            pass
                        case False:
                            aopm.info("User canceled. Aborting...")
                            return 1
            env = os.environ.copy()
            env["aoproot"] = "/"
            aopm.info("Executing pre-install triggers...")
            pre_install_try = sub.run(["bash", f"{tmp}/extract2/aopkg-tools/install.sh", "pre_install"], env=env, capture_output=True)
            if pre_install_try.returncode == 0:
                aopm.success("Pre-install triggers executed!")
            else:
                aopm.error(f"Failed to execute pre-install triggers :(. Exit code: {pre_install_try.returncode}", True)
            aopm.info("Installing package...")
            
            install_try = sub.run(["bash", f"{tmp}/extract2/aopkg-tools/install.sh", "install"], env=env, capture_output=True)
            if install_try.returncode == 0:
                aopm.success("Package installed!")
            else:
                aopm.error(f"Failed to install package :(. Exit code: {install_try.returncode}", True)

            aopm.info("Executing post-install triggers...")
            post_install_try = sub.run(["bash", f"{tmp}/extract2/aopkg-tools/install.sh", "post_install"], env=env, capture_output=True)
            if post_install_try.returncode == 0:
                aopm.success("Post-install triggers executed!")
            else:
                aopm.error(f"Failed to execute post-install triggers :(. Exit code: {post_install_try.returncode}", True)

            
            aopm.info("Adding package to 'installed packages'...")
            packages_path = args[4]
            pkg_dir = f"{packages_path}/{package_to_search}"

            if os.path.exists(pkg_dir):
                aopm.warn("Direcotry already exists. Removing...")
                shutil.rmtree(pkg_dir)
            
            os.makedirs(pkg_dir)
            
            shutil.copy(f"{tmp}/extract2/aopkg.json", f"{pkg_dir}/aopkg.json")
            shutil.copy(f"{tmp}/extract2/file-list", f"{pkg_dir}/file-list")
            
            aopm.success("Package added to 'installed packages!'")
            aopm.success("Everything looks done!")
            return 0
        else:
            aopm.info("User canceled. Aborting...")
            return 1

def help():
    title_line = f"{header["name"]}-{header["version"]} Module"
    print(f"""
{title_line}
{"=" * (len(title_line) + 1)}

Description:
-------------
    Allows you to install pacakges from initialized repositories.

Usage:
-------
    aopm install <package> [options]

Example(s):
----------
    aopm install grub-efi    Install the 'grub-efi' package.
    aopm install aopkg       Install the 'aopkg' package.

Notes:
-------
    You can only install one package at time.
""")