# qpasteboard

Version 0.9 - may still have issues

(Python) Qt5 Clipboard.

Free to use and modify.

Qpasteboard is a clipboard program for Linux. The main program and its applet are built using Python3 and the Qt5 libraries. No additional modules are required.

Qpasteboard can store and set pieces of text and can store, set and save pictures (or disable this option in the config file). It can show the preview of the stored items, can delete each entry or the whole history.

As default option, the path names of the copied files and folders are not stored. This behaviour, and other settings, can be changed in the config file.

This program has an option that discharges all text over a certain lenght (actually 1000 characters), unless this option is setted to 0.

All clipboards are stored in text files, that can be modified with a text editor; because this program store statically the mini previews internally (instead of the full texts for fast loading and less resources usage), after a modification of the files, this program needs to be restarted to update the mini previews.

To execute this program from the terminal: ./qpasteboard.sh or python3 qpasteboard.py

![My image](https://github.com/frank038/qpasteboard/blob/main/screenshot1.png)

![My image](https://github.com/frank038/qpasteboard/blob/main/screenshot2.png)
