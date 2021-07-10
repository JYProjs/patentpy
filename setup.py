from setuptools import setup

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
from os import path

import sys

def read(rel_path):
    with open(path.join(path.abspath(path.dirname(__file__)), rel_path), 'r') as f:
        return f.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

def get_long_desc(rel_path):
    with open(path.join(path.abspath(path.dirname(__file__)), rel_path), 'r', encoding="utf-8") as f:
        return f.read()

__version__ = get_version("patentpy/__init__.py")

ext_modules = [
    Pybind11Extension("convert_funcs",
        ["src/convert_funcs.cpp", "src/wrapper.cpp"],
        cxx_std=11,
        define_macros = [('VERSION_INFO', __version__)],
        ),
]

setup(
    name = "patentpy",
    version = __version__,
    author = "James Yu, Raoul Wadhwa, Hayley Beltz, Milind Y. Desai, Jacob G. Scott, Peter Erdi",
    author_email = "jyu140@jhu.edu",
    description = "A project taking USPTO bulk patent data and converting it to rectangular format",
    long_description = get_long_desc('README.md'),
    long_description_content_type = "text/markdown",
    url = "https://github.com/JYProjs/patentpy",
    packages = ["patentpy"],
    ext_modules = ext_modules,
    install_requires = ["pandas", "lxml"],
    classifiers = [
            "Programming Language :: Python :: 3",
            "Programming Language :: C++",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Intended Audience :: Science/Research",
            "Intended Audience :: Information Technology",
            "Intended Audience :: Legal Industry",
            "Natural Language :: English",
            "Topic :: Utilities",
            "Topic :: Text Processing :: General",
            "Topic :: Text Processing :: Markup :: XML",
            ],
    license = "MIT",
    zip_safe = False,
    python_requires = ">=3.5",
)
