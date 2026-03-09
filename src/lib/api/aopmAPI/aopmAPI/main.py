"""

AOPM (Axok!_OS Package Manager) API
Version: 1.0.0
Made by: GusDev

"""

# libs
# -----
#   All the libs that the AOPM API will use
#   ex: sys

import sys


# Global variables
# -----------------

# the API Version is 1.0.0
__version__ = (1, 0, 0)

# Print Defs
# -----------
#   Print infos, successes, errors, warnings
#   ex: info("running api...")

def info(msg : str = "") -> None:
    """
    Print an info message

    :param msg: The message that will be printed
    :type msg: str
    :return: None
    """
    print(f"=> \033[36m[INFO]\033[0m: {msg}")

def success(msg : str = "") -> None:
    """
    Print an success message

    :param msg: The message that will be printed
    :type msg: str
    :return: None
    """
    print(f"==> \033[32m[SUCCESS]\033[0m: {msg}")

def warn(msg : str = "") -> None:
    """
    Print an warning message

    :param msg: The message that will be printed
    :type msg: str
    :return: None
    """
    print(f"=> \033[33m[WARNING]\033[0m: {msg}")

def error(msg : str = "", exit : bool = False) -> None:
    """
    Print an error message

    :param msg: The message that will be printed
    :type msg: str
    :param exit: If True exit the code
    :type exit: bool
    :return: None
    """
    print(f"==> \033[31m[ERROR]\033[0m: {msg}")
    if exit:
        sys.exit(1)

# the header reader class
class Api_header():
    """
    Read and check an API Header

    :def __init__: get an header and read
    :def check: check if the API Header is valid to go
    """
    def __init__(self, header : list):
        """
        Get the header and prepare

        :param header: The heaer to be readed
        :type header: list
        :return bool:
        """

        # The essential keys
        # -------------------
        #   If the header dont have anyone of the essential keys
        #   it will not work

        essential_keys = [
            "name",
            "version",
            "description",
            "author",
            "author_email",
            "api_version"
        ]

        # the extra keys
        # ---------------
        #   if the header have ok, if dont have no problem

        extra_keys = [
            "license"
        ]

        # check the keys
        
        for key in essential_keys:
            if key not in header:
                error(f"The header dont have: '{key}' :(")
                sys.exit(1)
            else:
                if str(header[key]).strip().lower() == "":
                    error(f"The key: '{key}' is empty :(")
                    sys.exit(1)
                else:
                    setattr(self, key, header[key])

        for key in extra_keys:
            if key in header:
                if str(header[key]).strip().lower() == "":
                    pass
                else:
                    setattr(self, key, header[key])
        
        # transform the api_version into a tuple
        try:
            self.api_version = tuple(map(int, header["api_version"].split(".")))
        except Exception:
            error(f"Invalid API Version: '{header["api_version"]}' :(")
            sys.exit(1)
            
        # done!
    
    def check(self) -> bool:
        """
        Check the API Header

        :return bool:
        """

        # check the api_version
        if self.api_version > __version__:
            error("The module want a newer version on the API :(")
            sys.exit(1)
        else:
            return True