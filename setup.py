"""
Установочный скрипт для пакета TravelPlanner.

Этот скрипт настраивает приложение TravelPlanner для установки
с использованием setuptools, что позволяет установить его как Python-пакет.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Чтение содержимого README файла
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(
    encoding='utf-8') if readme_file.exists() else ''

# Чтение зависимостей из requirements.txt
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip(
        ) and not line.startswith('#')]

setup(
    name='travelplanner',
    version='1.0.0',
    author='TravelPlanner Team',
    author_email='info@travelplanner.com',
    description='TravelPlanner - веб-приложение для планирования путешествий',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/travelplanner',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.9',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-flask>=1.2.0',
            'coverage>=7.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
        'docs': [
            'sphinx>=7.2.6',
            'sphinx-rtd-theme>=1.3.0',
        ],
        'postgresql': [
            'psycopg2-binary>=2.9.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'travelplanner=run:main',
        ],
    },
    package_data={
        'app': [
            'templates/*.html',
            'static/css/*.css',
            'static/js/*.js',
        ],
    },
    zip_safe=False,
)
