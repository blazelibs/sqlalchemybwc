import os
from setuptools import setup, find_packages

# pip install -e .[develop]
develop_requires = [
    'WebTest',
]

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()
VERSION = open(os.path.join(cdir, 'sqlalchemybwc', 'version.txt')).read().strip()

setup(
    name='SQLAlchemyBWC',
    version=VERSION,
    description="An SQLAlchemy component for BlazeWeb applications",
    long_description='\n\n'.join((README, CHANGELOG)),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: BSD License',
    ],
    author='Randy Syring',
    author_email='randy.syring@level12.io',
    url='https://github.com/blazelibs/sqlalchemybwc/',
    license='BSD',
    packages=['sqlalchemybwc'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'pathlib',
        # need session cleanup event support from BlazeWeb
        'BlazeWeb>=0.4.9',
        'SAValidation >=0.2.0',
        'six',
    ],
    extras_require={'develop': develop_requires},
)
