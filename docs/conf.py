# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys


# -- Project information -----------------------------------------------------

project = 'patentpy'
copyright = '2021, James Yu'
author = 'James Yu'

# The full version, including alpha/beta/rc tags
def read(rel_path):
    root_dir = os.path.join(os.path.dirname(__file__), "..")
    ver_file_path = os.path.join(os.path.abspath(root_dir), rel_path)
    with open(ver_file_path, 'r') as f:
        return f.read()
        
def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

release = get_version("patentpy/__init__.py")


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon'
]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = False
napoleon_type_aliases = None

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'setup.py', 'tests-python', '.circleci', 'dist', 'patentpy.egg-info']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']