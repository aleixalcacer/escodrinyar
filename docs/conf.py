# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from seaborn._core.properties import PROPERTIES

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'escodrinyar'
copyright = '2024, Aleix Alcacer'
author = 'Aleix Alcacer'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "numpydoc",
    "myst_nb"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_title = "Escodrinyar"
html_logo = "_static/escodrinyar.png"

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/aleixalcacer/escodrinyar",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        }
    ]
}

# -- Extensions configuration ------------------------------------------------

# myst configuration
myst_enable_extensions = [
    "colon_fence",
]
nb_execution_mode = "off"
jupyter_execute_notebooks = "off"

# Intersphinx params
intersphinx_mapping = {
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'statsmodels': ('https://www.statsmodels.org/stable/', None),
    'seaborn': ('https://seaborn.pydata.org/', None),
}

# The reST default role (used for this markup: `text`) to use for all documents.
default_role = 'literal'

# Generate the API documentation when building
autosummary_generate = True
numpydoc_show_class_members = False

# Sphinx-issues configuration
issues_github_path = 'aleixalcacer/escodrinyar'

# Include the example source for plots in API docs
plot_include_source = True
plot_formats = [('png', 90)]
plot_html_show_formats = False
plot_html_show_source_link = False

# Don't add a source link in the sidebar
html_show_sourcelink = False

# Control the appearance of type hints
autodoc_typehints = "none"
autodoc_typehints_format = "short"

# Define replacements (used in whatsnew bullets)
rst_epilog = r"""

.. role:: raw-html(raw)
   :format: html

.. role:: raw-latex(raw)
   :format: latex

.. |API| replace:: :raw-html:`<span class="badge badge-api">API</span>` :raw-latex:`{\small\sc [API]}`
.. |Defaults| replace:: :raw-html:`<span class="badge badge-defaults">Defaults</span>` :raw-latex:`{\small\sc [Defaults]}`
.. |Docs| replace:: :raw-html:`<span class="badge badge-docs">Docs</span>` :raw-latex:`{\small\sc [Docs]}`
.. |Feature| replace:: :raw-html:`<span class="badge badge-feature">Feature</span>` :raw-latex:`{\small\sc [Feature]}`
.. |Enhancement| replace:: :raw-html:`<span class="badge badge-enhancement">Enhancement</span>` :raw-latex:`{\small\sc [Enhancement]}`
.. |Fix| replace:: :raw-html:`<span class="badge badge-fix">Fix</span>` :raw-latex:`{\small\sc [Fix]}`
.. |Build| replace:: :raw-html:`<span class="badge badge-build">Build</span>` :raw-latex:`{\small\sc [Deps]}`

"""  # noqa


# TODO: Add tilewidth and tileheight
rst_epilog += "\n".join([
    f".. |{key}| replace:: :ref:`{key} <{val.__class__.__name__.lower()}_property>`"
    for key, val in PROPERTIES.items()
])
