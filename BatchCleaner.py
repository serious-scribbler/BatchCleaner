import platform
import ctypes
import sys
import eel
import os
import random
import string
import jsonpickle
from pathlib import Path

from app.model import DirectoryListItem

eel.init("web")


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

paths = {}
stats = {}

cleaner_dir = os.path.join(os.path.abspath(Path.home()), "BatchCleaner")
path_file = os.path.join(cleaner_dir, "paths.json")
stats_file = os.path.join(cleaner_dir, "stats.json")

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


def update_stats(path: str, data: int):
    if path not in stats:
        stats[path] = data
    else:
        stats[path] += data


def start_application():
    eel.start("templates/clean.htm", size=(1280, 720), jinja_templates="templates")
    eel.say_hello()


def get_random_id():
    id = ""
    while id == "" or id in paths:
        id = "".join(random.choices(string.ascii_uppercase, k=5))


@eel.expose
def change_path(id: str, path: str):
    if id not in paths:
        pass # Call error display
    elif os.path.isdir(path):
        paths[id].path = path


@eel.expose
def add_path(path: str):
    if os.isdir(path):
        id = get_random_id()
        paths[id] = DirectoryListItem(id, paths, path)
        # TODO: Call callback
    else:
        pass # Call error function


@eel.expose
def delete_path(id: str):
    if id in paths:
        del paths[id]
        # TODO; call callback


@eel.expose
def set_recursive(id: str, recursive:bool):
    if id not in paths:
        pass # TODO: Call error callback
    else:
        paths[id].recursive == recursive


@eel.expose
def get_paths():
    for p in paths:
        pass # TODO call callback


@eel.expose
def get_stats() -> str:
    return object_to_json(stats, unpicklable=False)


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

