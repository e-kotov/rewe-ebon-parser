# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pathlib
import sys
from recommonmark.parser import CommonMarkParser

sys.path = [
    str(pathlib.Path().resolve()),
    str(pathlib.Path().resolve() / "_extensions"),
] + sys.path



# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'rewe-ebon-parser'
copyright = '2024, Egor Kotov'
author = 'Egor Kotov'
release = '0.0.7'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration



extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    "sphinx_autodoc_typehints",
    'sphinx_rtd_theme',
    'recommonmark',
]

autosummary_generate = True
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ['_templates']
exclude_patterns = ['_build', '_static', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_title = "rewe-ebon-parser"
html_short_title = "rewe-ebon-parser"

html_static_path = ["_static"]
html_last_updated_fmt = "%Y-%m-%d"


# html_theme_options = {
#     "collapse_navigation": False,
#     "navigation_with_keys": False,
#     "path_to_docs": "docs",
#     "repository_branch": "main",
#     "repository_url": "https://github.com/e-kotov/rewe-ebon-parser/",
#     "use_edit_page_button": True,
#     "use_repository_button": True,
# }

master_doc = 'index'


source_parsers = {
    '.md': CommonMarkParser,
}

source_suffix = ['.rst', '.md']
