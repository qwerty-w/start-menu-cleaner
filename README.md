# Start Menu Cleaner
### Installation:
Choose one of the ways:
- [Download](https://github.com/qwerty-w/start-menu-cleaner/releases) the latest version of the executable file from the releases.
- Run from the Python interpreter:
```commandline
python3 -m pip install -r requirements.txt
python3 start.py
```
- Using pyinstaller, build the executable file:
```commandline
python3 -m pip install -r requirements.txt pyinstaller
pyinstaller start.spec
```
### Usage:
- Available optional arguments:
```commandline
usage: Start Menu Cleaner [-h] [--logging {full,cleaning}] [--style {classic,material}]

optional arguments:
  -h, --help            show this help message and exit
  --logging {full,cleaning}
                        full - recording full work in a single file, cleaning - recording only the clean process to a file (each cleaning is a new file), temp file path example - C:\Users\user\AppData\Local\Temp\sm-<name>-<timestamp>.log       
  --style {classic,material}
                        classic - default Windows style, material (by-default) - material style
```
### Examples:

