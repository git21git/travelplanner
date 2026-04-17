import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../app'))

# -- Project information ----------------------------------------
project = 'TravelPlanner'
copyright = '2024, TravelPlanner Team'
author = 'TravelPlanner Team'
version = '1.0'
release = '1.0.0'

# -- General configuration --------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # Для директивы .. automodule::
    'sphinx.ext.napoleon',     # Для Google стиля docstrings
    'sphinx.ext.viewcode',     # Для ссылок на исходный код
]

# Язык
language = 'ru'

# Паттерны исключения
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output ------------------------------------
html_theme = 'sphinx_rtd_theme'

# -- Options for autodoc ----------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
}

# Моки для импорта (чтобы Sphinx не пытался импортировать Flask)
autodoc_mock_imports = [
    'flask',
    'flask_sqlalchemy',
    'flask_login',
    'flask_wtf',
    'wtforms',
    'requests',
]
