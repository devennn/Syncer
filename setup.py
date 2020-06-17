from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession

setup(
    name='Syncer-cli',
    version = '0.1.0',
    packages = ['syncer'],
    install_requires = [
        'PySimpleGUI==4.20.0'
    ],
    entry_points = {
        'console_scripts': ['syncer = syncer.__main__:main']
    }
)