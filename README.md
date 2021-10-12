# BatchCleaner
BatchCleaner is a batch deletion tool that allows the user to quickly delete files in different locations with the push of a single button.
Paths only need to be added once and will stay saved for the next time BatchCleaner is used. BatchCleaner also collects statistics on the amount of data deleted from each directory.

## Screenshots

### The main screen for adding directories and deleting the contained files
![Deletion screen](/screenshots/BeforeDeletion.png?raw=true "The deletion screen")

### The statistics screen that provides an insight into which directories are responsible for most of the deleted data
![Stats](/screenshots/Stats.png?raw=true "Stats")

## How to use BatchCleaner
### Windows standalone exe
Download and run the .exe provided under the releases tab, add your directories and press the delete button.

### Python

#### 1. Open your terminal and create a virutal environment using venv:
```sh
python -m venv env
```
#### 2. Activate the environment:
##### On Windows:
```cmd
.\env\Script\activate
```
##### On Unix / MacOS
```sh
source env/bin/activate
```
#### 3. Install the requirements
```sh
pip install -r requirements.txt
```

#### 4. Run BatchCleaner
```sh
python BatchCleaner.py
```

#### 5. When you're done, deactivate your venv
```sh
deactivate
```
## How to build the .exe using pyinstaller
To utilize eel's built in support for pyinstaller to build a Windows executable use the following command:

```cmd
python -m eel .\BatchCleaner.py .\web\ --uac-admin --onefile --noconsole --splash .\logo\splash.png -i .\logo\favicon.ico
```

This is currently the only way to delete files that require elevated priviledges on Windows. I implemented a method to get elevated priviledges, but the method I used, which worked in a small prototype no longer works in the actual program. If you know why runas returns an access denied error for the venvs python interpreter, please let me know.

