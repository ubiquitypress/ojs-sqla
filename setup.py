#!/usr/bin/env python

from distutils.core import setup


def readme():
    with open('README.md') as f:
        return f.read()


kwargs = {
    'name': 'ojssqla',
    'version': '0.0.5',
    'description': "Comfortable clothing for PKPs OJS",
    'keywords': 'Ubiquity Press PKP OJS',
    'author': 'Andy Byers',
    'author_email': 'tech@ubiquitypress.com',
    'url': 'https://github.com/ubiquitypress/ojs-sqla',
    'license': 'GPL 2',
    'packages': ['ojssqla'],
    # setuptools/pip args
    'zip_safe': False,
    'install_requires': [],
}

setup(**kwargs)
