# weckr
*A CLI alarm clock* — still under development


## Installation

Please make sure you have installed following dependencies beforehand:

- python3
- pip
- setuptools
- virtualenv (just for development)

1. Clone repository:
```
$ git clone https://github.com/foobar0112/weckr
$ cd weckr
```

2a. For development only: create virtual environment:
```
$ virtualenv venv
$ . venv/bin/activate
$ pip3 install --editable .
```
To exit virtualenv run `deactivate`.

2b. In production: Install weckr and dependencies (Click, python-vlc, python-dateutil) directly via setuptools:
```
$ sudo pip3 install --editable .
```

You now can use your weckr (in your virtualenv) simply with `weckr SOUND_FILE`, enjoy.


## Usage

```
Usage: weckr [OPTIONS] SOUND_FILE

  command line alarm clock takes audio file or directory of audio files

Options:
  -t, --time TEXT          Takes alarm time (h:m).
  -n, --news               Includes latest DLF news (default: 5 min delay).
  -N, --news-time INTEGER  Includes latest DLF news with specific time delay (in min).
  -v, --verbose            Toggles verbose mode.
  --help                   Show this message and exit.
```


## Update

Just pull the repository:
```
$ cd weckr
$ git pull
```


## Contribute

always welcome, use issues