# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

project = 'XAIoGraphs'
copyright = '2023, Telefonica'
author = 'Telefonica'

# The full version, including alpha/beta/rc tags
__VERSION__ = open('../../VERSION').read().strip()
release = __VERSION__
version = __VERSION__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'autodocsumm',
    'sphinx.ext.napoleon',
    'sphinx.ext.coverage',
    'myst_parser'
]

# Configuration of sphinx.ext.coverage
coverage_ignore_functions = [
    'test($|_)',
]

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%x'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store', '**tests**', '**test**']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'furo'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Force Sphinx to show __init__'s documentation
# autodoc_default_options = {
#     'members': True,
#     'member-order': 'bysource',
#     'undoc-members': True,
#     'exclude-members': '__weakref__',
#     'autosummary': True
# }

autodoc_default_options = {
    'members': True,
    'autosummary': True,
    'inherited-members': True
}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = '../imgs/icon.png'
html_favicon = '../imgs/favicon.ico'
html_title = 'XAIoGraphs <br/> {}'.format(__VERSION__)
html_css_files = ['css/custom.css']

# LaTeX
myst_enable_extensions = ["dollarmath", "amsmath"]
