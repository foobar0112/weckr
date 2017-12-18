from setuptools import setup

setup(
    name='weckr',
    version='0.1',
    py_modules=['weckr'],
    install_requires=[
        'Click',
        'python-vlc',
        'python-dateutil'
    ],
    entry_points='''
        [console_scripts]
        weckr=weckr:weckr
    ''',
)
