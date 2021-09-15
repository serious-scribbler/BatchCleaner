import platform
import ctypes
import sys
from bottle import load
import eel
import os
import random
import string
import jsonpickle
import webbrowser
from pathlib import Path

from app.model import DirectoryListItem

eel.init("web")

file_sizes = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

paths = {}
stats = {"total": 0, "individual": {}}

cleaner_dir = os.path.join(os.path.abspath(Path.home()), ".BatchCleaner")
path_file = os.path.join(cleaner_dir, "paths.json")
stats_file = os.path.join(cleaner_dir, "stats.json")


def get_dir_size(d):
    total_size = 0
    for entry in os.scandir(d):
        if entry.is_file():
            total_size += entry.stat().st_size
        elif entry.is_dir():
            total_size += get_dir_size(entry.path)
    return total_size


def size_to_string(s):
    size = float(s)
    unit_counter = 0
    while size > 1024:
        size = size / 1024.0
        unit_counter += 1
    return "" + str(round(size, ndigits=2)) + " " + file_sizes[unit_counter]


def object_to_json(obj, unpicklable=True )-> str:
    jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
    return jsonpickle.dumps(obj, indent=4, unpicklable=unpicklable)


def object_to_json_file(obj, path: str) -> None:
    with open(path, mode="w") as f:
        f.write(object_to_json(obj))


def load_from_disk():
    global paths, stats
    try:
        if os.path.isfile(path_file):
            with open(path_file) as f:
                paths = jsonpickle.decode(f.read())
        if os.path.isfile(stats_file):
            with open(stats_file) as f:
                stats = jsonpickle.decode(f.read())
    except Exception as e:
        print("Unable to load config files ", e)


def save_paths():
    os.makedirs(cleaner_dir, exist_ok=True)
    object_to_json_file(paths, path_file)


def save_stats():
    os.makedirs(cleaner_dir, exist_ok=True)
    object_to_json_file(stats, stats_file)


def update_stats(path: str, data: float):
    if path not in stats["individual"]:
        stats["individual"][path] = round(data, ndigits=2)
    else:
        stats["individual"][path] += round(data, ndigits=2)


def start_application():
    load_from_disk()
    eel.start("templates/clean.htm", size=(1280, 720), jinja_templates="templates")
    


def get_random_id():
    id = ""
    while id == "" or id in paths:
        id = "".join(random.choices(string.ascii_uppercase, k=5))
    return id


@eel.expose
def change_path(id: str, path: str):
    if path == None:
        eel.triggerAlert(path + " is not a directory!", "Error", "red")
        return False
    if id not in paths:
        eel.triggerAlert("This entry doesn't exist!", "Error", "red")
        return False
    elif os.path.isdir(path):
        try:
            size = size_to_string(get_dir_size(path))
            paths[id].path = path
            eel.setSize(id, size)
            save_paths()
            return True
        except:
            eel.triggerAlert("Access denied!", "Error", "red")
            return False
    else:
        eel.triggerAlert(path + " is not a directory!", "Error", "red")
        return True


@eel.expose
def add_path(path: str):
    if path == None:
        eel.triggerAlert(path + " is not a directory!", "Error", "red")
        return
    if os.path.isdir(path):
        try:
            size = size_to_string(get_dir_size(path))
            id = get_random_id()
            paths[id] = DirectoryListItem(id, paths, path)
            eel.addPath(id, path, paths[id].recursive, size)
            save_paths()
        except Exception as e:
            eel.triggerAlert(str(e), "Error", "red")
    else:
        eel.triggerAlert(path + " is not a directory!", "Error", "red")


@eel.expose
def delete_path(id: str):
    if id in paths:
        del paths[id]
        save_paths()
    else:
        eel.triggerAlert("This entry doesn't exist!", "Error", "red")


@eel.expose
def set_recursive(id: str, recursive:bool):
    if id not in paths:
        eel.triggerAlert("This entry doesn't exist!", "Error", "red")
    else:
        paths[id].recursive = recursive
        save_paths()


@eel.expose
def get_paths():
    for k, p in paths.items():
        eel.addPath(p.id, p.path, p.recursive, size_to_string(get_dir_size(p.path)))


@eel.expose
def get_stats():
    return [size_to_string(stats["total"]), list(stats["individual"].keys()), list(stats["individual"].values())]


"""
Returns size of deleted file
"""
def delete_file(path:str) -> int:
    try:
        size = Path(path).stat().st_size
        os.remove(path)
        return size
    except Exception as e:
        eel.logText("Unable to delete " + path + " - " + str(e), "red")
        return 0

"""
Returns the total size of all deleted files
"""
def clean_dir(path:str, recursive:bool) -> int:
    deleted_size = 0
    eel.logText("Processing " + path, "white")
    for entry in os.scandir(path):
        if entry.is_file():
            deleted_size += delete_file(entry.path)
        elif recursive and entry.is_dir():
            deleted_size += clean_dir(entry.path, recursive=recursive)
            try:
                os.rmdir(entry.path)
            except Exception as e:
                eel.logText("Unable to delete directory " + entry.path + " - " + str(e), "orange")
    return deleted_size


def _run_cleaner():
    eel.disableInput()
    eel.logText("Starting cleaning process...", "blue")
    total_size = 0
    for id, path_obj in paths.items():
        size = clean_dir(path_obj.path, path_obj.recursive)
        size_str = size_to_string(size)
        total_size += size
        update_stats(path_obj.path, int(size)/(1024*1024)) # Converting to MB
        eel.logText("Deleted " + size_str + " from " + path_obj.path)
        eel.setSize(id, size_to_string(get_dir_size(path_obj.path)))
    eel.logText("Successfully deleted a total of " + size_to_string(total_size), "green")
    eel.logText("Done")
    eel.enableInput()
    eel.success(size_to_string(total_size))
    stats["total"] += total_size
    save_stats()


def _open_repo_in_browser():
    webbrowser.open("https://github.com/serious-scribbler/BatchCleaner/", new=1)


@eel.expose
def clean_now():
    eel.spawn(_run_cleaner)


@eel.expose
def open_repo():
    eel.spawn(_open_repo_in_browser)


if __name__ == "__main__":
    start_application()
    exit(0)
    if platform.system() == "Windows":
        print(sys.argv)
        if not is_admin():
            args = " ".join(sys.argv if "python" in sys.executable else sys.argv[1:])
            print(args)
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            print("yar")
            start_application()
    else:
        start_application()

