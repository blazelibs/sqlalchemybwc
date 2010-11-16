"""
Introduction
---------------

CommonBWC is a component for `BlazeWeb <http://pypi.python.org/pypi/BlazeWeb/>`_
applications.

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

Current Status
---------------

The code stays pretty stable, but the API may change in the future.

The `CommonBWC tip <http://bitbucket.org/rsyring/sqlalachemybwc/get/tip.zip#egg=sqlalchemybwc-dev>`_
is installable via `easy_install` with ``easy_install sqlalchemybwc==dev``
"""

from setuptools import setup, find_packages

# has to be here b/c importing from the package gives us an import error if
# the venv isn't active
version = '0.1'

setup(
    name='SQLAlchemyBWC',
    version=version,
    description="An SQLAlchemy component for the BlazeWeb applications",
    classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    ],
    author='Randy Syring',
    author_email='rsyring@gmail.com',
    url='',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    zip_safe=False,
    install_requires=[
        'BlazeWeb>=0.3.0',
        'SQLAlchemy>=0.6.1',
        'savalidation>=0.1',
        'SQLiteFKTG4SA>=0.1.1'
    ],
)
