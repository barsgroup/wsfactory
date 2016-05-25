# -*- coding: utf-8 -*-
import os
from distutils.core import setup


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as fd:
        return fd.read()

setup(
    name='wsfactory',
    version='0.2.2',
    packages=['wsfactory', 'wsfactory.management',
              'wsfactory.management.commands'],
    package_dir={'': 'src'},
    package_data={'': ['schema/*']},
    url='http://bitbucket.org/barsgroup/wsfactory',
    license=read_file("LICENSE"),
    description=read_file("DESCRIPTION"),
    author='Timur Salyakhutdinov',
    author_email='t.salyakhutdinov@gmail.com',
    install_requires=read_file("REQUIREMENTS"),
)
