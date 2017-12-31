from setuptools import setup

setup(
    name='weckr',
    version='0.2',
    py_modules=['weckr'],
    install_requires=[
        'python-vlc',
        'python-dateutil'
    ],

    entry_points = {
        'console_scripts': ['weckr=weckr:main'],
    }
)
