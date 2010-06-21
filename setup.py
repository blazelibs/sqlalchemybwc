from setuptools import setup, find_packages

version = '0.1dev'

setup(
    name='SQLAlchemyBWP',
    version=version,
    description="An SQLAlchemy plugin for the BlazeWeb framework",
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
        'blazeweb>=dev',
        'SQLAlchemy>=0.5'
    ],
)
