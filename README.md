# journaling-filesystem

This is a filesystem that tracks changes in .txt files that I built in my Introduction to Operating Systems class.

Examples can be seen under the "Examples" directory.

The "Directory" folder is tracked by the filesystem, and the "Journal" folder is where the filesystem places the backups of each file for future rebuilding.

journal.py runs on a loop and tracks the "Directory" folder, while rebuild.py can be ran at any time to rebuild a file from the "Journal" folder.