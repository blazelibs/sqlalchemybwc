from setuptools import setup, find_packages

version = '0.1dev'

setup(
    name='SQLAlchemyBWC',
    version=version,
    description="An SQLAlchemy component for the BlazeWeb framework",
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
        'BlazeWeb>=0.3.0dev',
        'SQLAlchemy>=0.6.1',
        'savalidation>=dev',
        'SQLiteFKTG4SA>=0.1.1'
    ],
)
