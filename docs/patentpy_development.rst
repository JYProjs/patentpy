Development
===========

Release Info
------------
Current Version 0.2.0 changes:
 * refactored code for better maintainability
 * added progress bar
 * fixed bug where inappropriately coded chars in XML1 (2000-2002) files threw lxml parsing errors (bad characters replaced by � symbol)
 * fixed bug where TXT (1976-2001) claims text incorporated char \'\\x9b\' (replaced with '!' to match ending '!', possibly control for brackets based on manual confirmation with uspto patent search results)
 * fixed spacing in TXT claims text
 * output file encoding specified as 'utf-8'. See [issue](https://github.com/JYProjs/patentpy/issues/10)

Version >= 0.1.1 supports both TXT and XML conversions of USPTO bulk patent data (Full Text - no images) to csv and dataframe format.
This includes patent data from January of 1976 to present.


Contribute
----------

We welcome all feedback! To contribute to patentpy, you can create issues for any bugs/suggestions on the `issues page <https://github.com/JYProjs/patentpy/issues>`_.
You can also fork the patentpy repository and create pull requests to add features you think will be useful for users.

Citation
--------

Yu J, Wadhwa RR, Beltz H, Milind Y. Desai, Jacob G. Scott, Erdi P. patentpy: Access USPTO Bulk Data in Rectangular Format. 2021; Python package version 0.1.0. URL https://github.com/JYProjs/patentpy.

