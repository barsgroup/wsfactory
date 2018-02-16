# coding: utf-8
from os.path import join
from os.path import dirname

from pip.download import PipSession
from pip.req.req_file import parse_requirements
from setuptools import setup, find_packages


def _get_requirements(file_name):
    pip_session = PipSession()
    requirements = parse_requirements(file_name, session=pip_session)

    return tuple(str(requirement.req) for requirement in requirements)


def _read(fname):
    return open(join(dirname(__file__), fname)).read()


setup(
    name='wsfactory',
    url='https://stash.bars-open.ru/projects/M3/repos/wsfactory',
    license=_read("LICENSE"),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['schema/*']},
    classifiers=(
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django :: 1.4',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
    ),
    description=_read('DESCRIPTION'),
    author='Timur Salyakhutdinov',
    author_email='t.salyakhutdinov@gmail.com',
    install_requires=_get_requirements('REQUIREMENTS'),
    dependency_links=(
        'http://pypi.bars-open.ru/simple/m3-builder',
    ),
    setup_requires=(
        'm3-builder>=1.1',
    ),
    set_build_info=dirname(__file__),
)
