<p align="center">
  <img src="https://raw.githubusercontent.com/foobar0112/weckr/master/header.png" alt="Weckr Header"/>
</p>

*A CLI alarm clock* — still under development


## Installation

Please make sure you have installed following dependencies beforehand:

- [python3](https://www.python.org/downloads)
- [pip](https://pip.pypa.io/en/stable/installing)
- [setuptools](https://pypi.python.org/pypi/setuptools) (via pip)
- [virtualenv](https://virtualenv.pypa.io/en/latest/installation) (via pip, just for development)

(1) clone repository:
```
$ git clone https://github.com/foobar0112/weckr
$ cd weckr
```

(2a) for development only: create virtual environment:
```
$ virtualenv venv
$ . venv/bin/activate
$ pip3 install --editable .
```
To exit virtualenv run `deactivate`.

(2b) for production: Install dependencies ([python-vlc](https://pypi.python.org/pypi/python-vlc), [python-dateutil](https://pypi.python.org/pypi/python-dateutil/2.6.1)) and weckr directly via setuptools:
```
$ [sudo] pip3 install .
```

You now can use your weckr (in your virtualenv) simply with `weckr path/to/nice/technomix -t 8:00 -N 10`. \o/Wich will wake You up at 8 o'clock playing a nice techno mix and the latest [DLF news](http://www.deutschlandfunk.de) 10 minutes later.


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

Just pull the repository and run setuptools:
```
$ cd weckr
$ git pull
$ [sudo] pip3 install .
```


## Contribute

always welcome, use issues
