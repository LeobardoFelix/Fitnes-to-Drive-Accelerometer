# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
#sys.path.insert(0, os.path.abspath('../ConfigurationWindow'))
#sys.path.insert(0, os.path.abspath('../Graficadora'))
#sys.path.insert(0, os.path.abspath('../TestWindow'))
#sys.path.insert(0, os.path.abspath('../TestWindow/SerialCommunication'))
#sys.path.insert(0, os.path.abspath('../TestWindow/TestRutine'))
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'RTEMPUS'
copyright = '2026, Leobardo'
author = 'Leobardo'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'es'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
