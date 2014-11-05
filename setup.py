#!/usr/bin/env python

from distutils.core import setup

def readme():
    with open('README.md') as f:
        return f.read()

kwargs = {
	'name': 'sqla-ojs',
	'version': '0.0.1',
	'description': "Comfortable clothing for PKPs OJS",
	'keywords': 'Ubiquity Press PKP OJS',
	'author': 'Andy Byers',
	'author_email': 'andy.byers@ubiquitypress.com',
	'url': 'https://github.com/ubiquitypress/sqla-ojs',
	'license': 'GPL 2',
	'packages': ['sqla-ojs'],
	
	# setuptools/pip args
	
	'zip_safe': False, 		 	
	'install_requires': [

	],
}
setup(**kwargs)
