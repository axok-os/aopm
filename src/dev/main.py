"""

AOPM Package Builder
Version: 1.0.0
Made by: GusDev

"""

# libs:
# ------
#   All the libs that the program will use.

import sys
import shutil
import subprocess as sub
from pathlib import Path as p
import json
import os
import tarfile
import hashlib
import tempfile

try:
    import aopmAPI as aopm
except ImportError:
    print("Cant import the AOPM API :(")

# def to get the sha256
def get_sha(archive):
    sha256 = hashlib.sha256()

    with open(archive, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()

# simplify sys
argc = len(sys.argv)
argv = sys.argv

if argc <= 2:
    print("Too few arguments :(")
    sys.exit(1)

if os.geteuid() == 0:
    print("You cant execute aopkg as root :(")
    sys.exit(1)

action = sys.argv[1]
path = sys.argv[2]

# get the config_file this path probably will be edited by configure command
keys_path = "/home/gustavo/Projetos/axok-os/aopm/keys"

match action:
    case "init"|"create":
        # check if the path exists and if is a directory
        if p(path).is_dir():
            pass
        else:
            aopm.error("The specified path dont exist or is not a directory :(")
            sys.exit(1)

        # create the main files
        main_files = [
            f"{path}/files",
            f"{path}/aopkg-tools"
        ]
        try:
            for directory in main_files:
                os.makedirs(directory, exist_ok=True)
        except PermissionError:
            aopm.error("You dont have permission to create a aopkg on this directory :(", True)
            sys.exit(1)
        except FileExistsError:
            aopm.warn("Already exist an aopkg on this directory. This may cause fails.")
        
        aopkg_manifest = {
            "name": "your-package-name",
            "version": "1.0.0",
            "description": "Your package description.",
            "author": "Your Name.",
            "author_email": "your.email@here.com",
            "type": "package"
        }

        try:
            with open(f"{path}/aopkg.json", "w") as f:
                json.dump(aopkg_manifest, f)
        except PermissionError:
            aopm.error("You dont have permission to create a aopkg manifest on this directory :(", True)
            sys.exit(1)
        except FileExistsError:
            aopm.warn("Already exist an aopkg manifest. This may cause fails")
        
        install_file_content = """#!/usr/bin/env bash

# install.sh example

# this is the path of the script
script_dir="$(dirname "$(realpath "$0")")"
# this is your aopkg root
aopkg_root="$(realpath "$script_dir/..")"

# function to compile your source code before building the aopkg
compile() {
    # NOTE: $aoproot is a temporary root directory used during compilation.
    # Install your files inside "$aoproot" as if it were the real system root.
    # The AOPM will scan this directory to generate the list of installed files.

    # This is an example.
    # NOTE: this will be called to ONLY compile your source

    install -Dm755 "$aopkg_root/files/algo" "$aoproot/usr/bin/algo"
}

# function to install your files into the real system
install_def() {
    # NOTE: Here the '$aoproot' will be the system root

    # This is an example.
    # NOTE: this will install you program into the '$aoproot' for the files-list

    install -Dm755 "$aopkg_root/files/algo" "$aoproot/usr/bin/algo"
}

# function to use pre-install triggers to prepare the host pc
pre_install_def() {
    # here you can make your commands to prepare your package, like create users
    :
}

# function to user post_install triggers to make the final prepare for the host pc
post_install_def() {
    # here you can delete unused libs that your package install for example
    :
}

# use this for call the functions
case "$1" in
    compile)
        compile ;;
    install)
        install_def ;;
    pre_intall)
        pre_install_def ;;
    post_install)
        post_install_def ;;
esac"""

        try:
            with open(f"{path}/aopkg-tools/install.sh", "w") as f:
                f.write(install_file_content)
        except PermissionError:
            aopm.error("You dont have permission to create the install.sh on this directory :(", True)
            sys.exit(1)
        except FileExistsError:
            aopm.warn("Already exist an install.sh. This may cause fails")
            

        aopm.success("Aopkg project created!")
        aopm.success("Everything looks done!")
        sys.exit(0)

    case "compile":
        # check the archives and directories
        essential_dirs = [
            f"{path}/files",
            f"{path}/aopkg-tools"
        ]

        essential_files = [
            f"{path}/aopkg-tools/install.sh"
        ]

        for directory in essential_dirs:
            if p(directory).is_dir():
                pass
            else:
                aopm.error(f"The directory '{directory}' dont exist in package :(", True)
                sys.exit(1)
        
        for archive in essential_files:
            if p(archive).is_file():
                pass
            else:
                aopm.error(f"The file '{archive}' dont exist in package :(", True)
                sys.exit(1)
        
        # check if the install.sh and aopkg.json is empty
        with open(f"{path}/aopkg.json", "r") as f:
            if f.read() == "":
                aopm.error("The aopkg.json is empty :(", True)
                sys.exit(1)
        
        with open(f"{path}/aopkg-tools/install.sh", "r") as f:
            if f.read() == "":
                aopm.error("The install.sh is empty :(", True)
                sys.exit(1)
        
        # check if the install.sh calls the '$aoproot'
        with open(f"{path}/aopkg-tools/install.sh", "r") as f:
            content = f.read()
            
            if "$aoproot" in content:
                pass
            else:
                print("=> \033[33m[WARNING]\033[0m: The install.sh dont call '$aoproot'. This may cause fails")

        # check if the system have fakeroot
        if shutil.which("fakeroot"):
            print("==> \033[32m[SUCCESS]\033[0m: Fake root found!")
        else:
            aopm.error("Cant found the 'fakeroot' command :(", True)
            sys.exit(1)
        
        aopm.info("Calling 'compile()'...")

        os.makedirs(f"{path}/compile-build", exist_ok=True)
        env = os.environ.copy()
        env["aoproot"] = f"{path}/compile-build"
        compile_try = sub.run(["fakeroot", "sh", f"{path}/aopkg-tools/install.sh", "compile"], env=env, capture_output=True)
        if compile_try.returncode == 0:
            aopm.success("Package compiled!")
        else:
            aopm.error(f"Failed to compile package :(. Exit code: '{compile_try.returncode}'", True)
            sys.exit(1)
        
        aopm.info("Calling 'install()'...")
        install_try = sub.run(["fakeroot", "sh", f"{path}/aopkg-tools/install.sh", "install"], env=env, capture_output=True)
        if install_try.returncode == 0:
            aopm.success("Package installed!")
        else:
            aopm.error(f"Failed to install package :(. Exit code: '{install_try.returncode}'", True)
        
        aopm.info("Generating the file: 'file-list'...")
        try:
            with open(f"{path}/file-list", "w") as f:
                for root, dirs, archives in os.walk(f"{path}/compile-build"):
                    
                    # dirs
                    for d in dirs:
                        dir_path = os.path.relpath(os.path.join(root, d), f"{path}/compile-build")
                        f.write("/" + dir_path + "\n")
                        
                    # archives
                    for archive in archives:
                        file_path = os.path.relpath(os.path.join(root, archive), f"{path}/compile-build")
                        f.write("/" + file_path + "\n")
        except PermissionError:
            aopm.error("Dont have permission to create the file: 'file-list' on the directory :(", True)
        except FileExistsError:
            aopm.error("Already exist a 'file-list' file. This may cause fails", True)

        # check if the file-list is empty
        with open(f"{path}/file-list", "r") as f:
            if f.read() == "":
                aopm.error("The file 'file-list' is empty :(", True)

        aopm.success("'file-list' generated!")
        aopm.info("Compiling into '.aopkg.tar.xz'...")
        try:
            os.makedirs(f"{path}/final-compile", exist_ok=True)
        except PermissionError:
            aopm.error("Dont have permission to create the final-compile direcotry on the directory :(", True)
        except FileExistsError:
            aopm.error("Already exist a final-compile directory. This may cause fails", True)

        aopkg_manifest_content = {}
        try:
            with open(f"{path}/aopkg.json", "r") as f:
                aopkg_manifest_content = json.load(f)
        except PermissionError:
            aopm.error("Dont have permission to open the aopkg.json :(", True)

        if "name" in aopkg_manifest_content:
            pass
        else:
            aopm.error("The aopkg.json dont have the 'name' key :(", True)

        try:
            with tarfile.open(f"{path}/final-compile/{aopkg_manifest_content["name"]}.tar.xz", "w:xz") as tar:
                tar.add(f"{path}/aopkg-tools", arcname="aopkg-tools")
                tar.add(f"{path}/files", arcname="files")
                tar.add(f"{path}/aopkg.json", arcname="aopkg.json")
                tar.add(f"{path}/file-list", arcname="file-list")
        except PermissionError:
            aopm.error("Dont have permission to create the '.aopkg.tar.xz' file :(", True)
        except FileExistsError:
            aopm.error("Already exist an older '.aopkg.tar.xz' file :(", True)
        
        aopm.info("Generating SHA256...")
        try:
            with open(f"{path}/final-compile/sha256", "w") as f:
                f.write(get_sha(f"{path}/final-compile/{aopkg_manifest_content["name"]}.tar.xz"))
        except PermissionError:
            aopm.error("Dont have permission to create the 'sha256' file :(", True)
        except FileExistsError:
            aopm.error("Already exist an older 'sha256' file :(", True)
        
        aopm.success("SHA256 generated! ")

        aopm.info("Making final compile...")
        os.makedirs(f"{path}/final-compile/out", exist_ok=True)
        with tarfile.open(f"{path}/final-compile/out/{aopkg_manifest_content["name"]}.aopkg.tar.xz", "w:xz") as tar:
            tar.add(f"{path}/final-compile/{aopkg_manifest_content["name"]}.tar.xz", arcname=f"{aopkg_manifest_content["name"]}.tar.xz")
            tar.add(f"{path}/final-compile/sha256", arcname="sha256")
        aopm.success(f"Aopkg compiled in: '{path}/final-compile/out/{aopkg_manifest_content["name"]}.aopkg.tar.xz' :)")
        aopm.success("Everything looks done!")
        sys.exit(0)


