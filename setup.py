from setuptools import setup

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir

import sys

__version__ = "0.1.0"

ext_modules = [
    Pybind11Extension("convert_funcs",
        ["src/convert_funcs.cpp", "src/wrapper.cpp"],
        cxx_std=11,
        define_macros = [('VERSION_INFO', __version__)],
        ),
]

setup(
    name="patentpy",
    version=__version__,
    author="James Yu",
    author_email="jyu140@jhu.edu",
    url="https://github.com/JYProjs/patentpy",
    description="A project taking USPTO bulk patent data and converting it to rectangular format using pybind11",
    long_description="",
    ext_modules=ext_modules,
    zip_safe=False,
)
