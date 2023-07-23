# Start Menu Cleaner
### Description:
Start Menu Cleaner is a program designed to clean up folders endlessly created by 
installers. In addition, the application can become a full-fledged manager of the 
Windows start menu, with which you can rename, change, add new shortcuts.
<details>
  <summary>Microsoft Windows Defender</summary>
  Windows Defender swears at almost all programs compiled with 
  pyinstaller. The fact is that in reality pyinstaller packages 
  the Python interpreter and all the libraries used into a single 
  exe file. This and some other reasons is why such low-grade antiviruses 
  as Microsoft Defender identify the signature of the program collected 
  from Python sources as a threat. More details <a href="https://www.reddit.com/r/learnpython/comments/im3jrj/windows_defender_thinks_that_code_i_wrote_using">here</a>.
  <br>However, <a href="https://www.virustotal.com/gui/file/78e829a0f9e97f21b10562ad28746f564a8ad58ce6b808b48ff9afdc59d78be0">here</a> is the VirusTotal review.
  <br>You can also build the application yourself. The source code is in front of you.
</details>

### Preview:
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