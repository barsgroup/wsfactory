# coding: utf-8
import os

from pip.download import PipSession
from pip.req.req_file import parse_requirements
from setuptools import setup, find_packages


def _get_requirements(file_name):
    pip_session = PipSession()
    requirements = parse_requirements(file_name, session=pip_session)

    return tuple(str(requirement.req) for requirement in requirements)


def _read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__),
            fname)).read()
    except IOError:
        return ''


setup(
    name='wsfactory',
    url='http://bitbucket.org/barsgroup/wsfactory',
    license=_read("LICENSE"),
    packages=(
        'wsfactory',
        'wsfactory.management',
        'wsfactory.management.commands',
    ),
    package_dir={'': 'src'},
    package_data={'': ['schema/*']},
    description=_read('DESCRIPTION'),
    author='Timur Salyakhutdinov',
    author_email='t.salyakhutdinov@gmail.com',
    install_requires=_get_requirements('REQUIREMENTS'),
    dependency_links=(
        'http://pypi.bars-open.ru/simple/m3-builder',
    ),
    setup_requires=(
        'm3-builder>=1.0.1',
    ),
    set_build_info=os.path.dirname(__file__),
)
