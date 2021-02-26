from setuptools import setup

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir

import sys

__version__ = "0.1.0"

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

ext_modules = [
    Pybind11Extension("convert_funcs",
        ["src/convert_funcs.cpp", "src/wrapper.cpp"],
        cxx_std=11,
        define_macros = [('VERSION_INFO', __version__)],
        ),
]

classes = ["Programming Language :: Python :: 3", 
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",]

setup(
    name="patentpy",
    version=__version__,
    author="James Yu",
    author_email="jyu140@jhu.edu",
    description="A project taking USPTO bulk patent data and converting it to rectangular format using pybind11",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JYProjs/patentpy",
    ext_modules=ext_modules,
    install_requires=["pandas", "numpy"],
    classifiers=classes,
    zip_safe=False,
)
