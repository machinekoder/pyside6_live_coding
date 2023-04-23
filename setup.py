from setuptools import setup

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='pyside6-live-coding',
    version='1.0.0',
    packages=['pyside6_live_coding'],
    package_dir={'': 'src'},
    url='https://github.com/machinekoder/pyside6-live-coding/',
    license='MIT',
    author='Alexander Rössler',
    author_email='alex@machinekoder.com',
    description='Live coding for Python, Qt and QML',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['six', 'qtpy'],
    extras_require={
        'dev': [
            'pytest',
            'pytest-pep8',
            'pytest-cov',
            'pytest-qt',
            'black',
            'pre-commit',
        ]
    },
    scripts=['bin/pyside6-live-coding'],
    include_package_data=True,
)
