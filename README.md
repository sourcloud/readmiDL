# readmiDL

This is a simple python script that crawls read.mi, creates a folder structure and downloads all files. Its purpose is to automate the process of downloading all the files provided for my university courses automatically.

## Requirements

The script sends HTTP requests via **Requests** and uses **Beautiful Soup** with **lxml** to parse HTML.

Use following command to install requirements:

```shell
pip install -r requirements.txt
```

## How to use

Use following command to start the script:

```shell
python3 dlmi.py
```

You will be prompted to enter username and password of your HDS account. After you hit <kbd>Enter</kbd> the script will begin creating directories downloading files. It will skip already existing directories and files.

**Keep in mind:** Folder creation and file downloads will use the directory containing the ```dlmi.py``` file as starting point. Once started, it will keep on until finished, lost connection or manually interupted by pressing <kbd>CTRL</kbd>+<kbd>C</kbd>!

## Example of expected file tree

Following example shows the expected kind of directory structure after the script was used.

```shell
.
├── dlmi.py
├── requirements.txt
├── README.md
├── first course
    ├── subdirectory 1
    ├── file.pdf
    └── other_file.pdf
    └── subdirectory 2
    └── example.zip
├── second course
    ├── overview.pdf
    └── examples
    ├── archive
        └── old_example.py
    ├── some_file_in_between.txt
    └── current
        └── new_example.java
└── third course
    └── nothing2see.mp4
```
