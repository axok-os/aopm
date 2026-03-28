## aopmAPI Documentation

The aopmAPI is a simple and direct API made for AOPM, responsible by check the API headers, basic GPG verification and print informations.

### How to create a valid API header

To create a valid aopmAPI header, you will need some variables in a dict, like:

```json
{
  "name": "my-module",
  "version": "1.0.0",
  "description": "Your discription here.",
  "author": "Your Name.",
  "author_email": "you.email@here.com",
  "api_version": "1.0.0"
}
```

The keys:

- `"name"`: That is your module name.

- `"version"`: Your moudle version.

- `"description"`: Your module description.

- `"author"`: Your name.

- `"author_email"`: Your email.

- `"api_version"`: The API version your module need. If your version is newer than your version, it will make you module cant be runned.

> Note: all these keys is used by the module: 'module' to display informations about modules.

### Minimal estructure for your module

To your custom module work correctly you need some basic DEFs (functions):

- `get_header()`: Responsible to return your API header to the core for checks.

- `run()`: Responsible for your module actually runs.

- `help()`: Responsible to print your module help message like usage and examples.

> Note: the **help()** function is optional, but recommended.

There is a example:

```python
header = {
    "name": "your-module",
    "version": "1.0.0",
    "description": "Your description here.",
    "author": "Your Name.",
    "author_email": "your.email@here.com",
    "api_version": "1.0.0"
}

def get_header() -> dict:
    return header

def run(parameter : list *args) -> int:
    return 0

def help():
    print("Usage: aopm your-module <your parameter>")

```

In this example the `run()` function need to return a int value for the core exit with this value as exit code. The parameter **args** is used to receive extra parameters without crash by too much parameters.
