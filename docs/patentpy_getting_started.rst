.. role:: raw-html-m2r(raw)
   :format: html


Introduction and First Steps
============================
.. image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT


Overview
--------

The patentpy package allows easy access to USPTO (United States Patent and Trademark Office) bulk patent data in rectangular format. By downloading, converting, and storing patent data directly from the USPTO website, patentpy minimizes the work needed to acquire usable data, allowing users to focus on analyzing the data.

Installation
------------

.. code-block:: bash

   # install from PyPI
   pip install patentpy

   # To install development version
   # clone repository then run follow code from its parent directory
   pip install ./patentpy

Note: This package utilizes pybind11 to wrap a custom txt parser written in C++ code, lxml to parse xml files, and pandas for the option of presenting uspto bulk data as a dataframe.

Sample code
-----------

Bulk patent data in TXT format (1976-2001) can be downloaded using the year and week (within each year) as follows:

.. code-block:: python

   # import get_bulk_patent_data functionality
   from patentpy.python.acquire import get_bulk_patent_data


   # download patents from the first week of 1976 and get data frame
   patent_data = get_bulk_patent_data(year = 1976, week = 1)

   # download patents from the last 5 weeks of 1980
   # and store in a CSV file named "patent-data.csv"
   # Note: uspto patent data is reported on Tuesdays and 1980
   # has 53 Tuesdays, hence, 53 weeks worth of data
   get_bulk_patent_data(year = [1980]*5, week = range(49,54), output_file = "patent-data.csv")

Specific documentation of ``get_bulk_patent_data`` 's use can be found under "General Functions".

It is recommended to use ``get_bulk_patent_data`` (which calls ``convert_txt_to_df``) rather than 
calling ``convert_txt_to_df`` directly as the former better handles invalid arguments. 
Please carefully read the documentation if using ``convert_txt_to_df`` directly.

Functionality
-------------

Data collected for each patent
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* unique identifier (patent number - WKU)
* application date
* patent issue date
* patent title
* inventor name(s)
* assignee name(s)
* ICL classification (IPC or Locarno)
* referenced patent numbers
* claims