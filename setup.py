#!/usr/bin/python2
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re

import os, re;
with open(os.path.join(os.path.dirname(__file__), 'pythonvideoannotator_module_idtrackerai','__init__.py')) as fd:
	version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)


setup(
	name='Python video annotator - module - IdTrackerAI',
	version=version,
	description="""""",
	author=['Ricardo Ribeiro'],
	author_email='ricardojvr@gmail.com',
	url='https://github.com/UmSenhorQualquer/pythonvideoannotator-module-idtrackerai',
	packages=find_packages(),
    entry_points={
        'console_scripts': [
            'idtrackerai2annotator=pythonvideoannotator_module_idtrackerai.__main__:run',
        ],
    }
)
