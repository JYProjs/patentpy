# patentpy: Access USPTO data in Rectangular Format

|       CI          | status  |
|-------------------|---------|
| Linux Travis      | [![Build Status][travis_badge]][travis_url] |
| code coverage     | [![codecov][codecov_badge]][codecov_url]  |

[codecov_badge]:     https://codecov.io/gh/JYProjs/patentpy/branch/main/graph/badge.svg?token=OZWS94028B
[codecov_url]:       https://codecov.io/gh/JYProjs/patentpy
[travis_badge]:      https://travis-ci.com/JYProjs/patentpy.svg?branch=main
[travis_url]:        https://travis-ci.com/JYProjs/patentpy

<!-- TO-DO table for CI and pip wheel -->
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

The patentpy package allows easy access to USPTO (United States Patent and Trademark Office) bulk patent data in rectangular format. By downloading, converting, and storing patent data directly from the USPTO website, patentpy minimizes the work needed to acquire usable data, allowing users to focus on analyzing the data.

## Installation

```bash
# install from PyPI
pip install patentpy

# install from Anaconda -- TO-DO


To install development version
# clone repository then run follow code from its parent directory
pip install ./patentpy
```
<!-- DOES IT? -->
Note that this uses pybind11 to wrap C++ code in python. Please see system requirements for pybind11.

## Sample code

Bulk patent data in TXT format (1976-2001) can be downloaded using the year and week (within each year) as follows:

```python
# import get_bulk_patent_data functionality
from patentpy.python.acquire import get_bulk_patent_data


# download patents from the first week of 1976 and get data frame
patent_data = get_bulk_patent_data(year = 1976, week = 1)

# download patents from the last 5 weeks of 1980
# and store in a CSV file named "patent-data.csv"
# Note: uspto patent data is reported on Tuesdays and 1980
# has 53 Tuesdays, hence, 53 weeks worth of data
get_bulk_patent_data(year = [1980]*5, week = range(49,54), output_file = "patent-data.csv")
```

## Functionality

### Data collected for each patent

* patent title
* application date
* patent issue date
* text in patent abstract
* inventor name(s)
* assignee name(s)
* ICL classification
* unique identifier (AKA patent number)
* referenced patent numbers

## Contribute

To contribute to patentpy, you can create issues for any bugs/suggestions on the [issues page](https://github.com/JYProjs/patentpy/issues).
You can also fork the patentpy repository and create pull requests to add features you think will be useful for users.

## Citation

Yu J, Wadhwa RR, Erdi P. patentpy: Access USPTO Bulk Data in Rectangular Format. 2021; Python package version 0.1.0. URL https://github.com/JYProjs/patentpy.
