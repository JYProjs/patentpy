from setuptools import setup

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
from os import path

import sys

__version__ = "0.1.0"

curr_directory = path.abspath(path.dirname(__file__))
with open(path.join(curr_directory, 'README.md'), encoding="utf-8") as f:
    long_description = f.read()

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
    author="James Yu, Raoul Wadhwa, Peter Erdi",
    author_email="jyu140@jhu.edu",
    description="A project taking USPTO bulk patent data and converting it to rectangular format using pybind11",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JYProjs/patentpy",
    packages = ["python"],
    ext_modules=ext_modules,
    install_requires=["pandas", "numpy"],
    classifiers= [
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
            ],
    zip_safe=False,
    python_requires='>=3',
)
