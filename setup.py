#!/usr/bin/env python
from setuptools import setup

requirements = []
with open('./requirements.txt', 'r') as fp:
    requirements = [l.strip() for l in fp]

long_description = ''
with open('./README.rst', 'r') as fp:
    long_description = fp.read()


setup(
    name='soup-schema',
    version='0.1.0',
    py_modules=[
        'soup_schema',
    ],
    install_requires=requirements,

    author='Brett Langdon',
    author_email='me@brett.is',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
    ],
    description='',
    license='MIT',
    long_description=long_description,
    keywords='beautifulsoup, soup, html, parser, schema',
    url='https://github.com/brettlangdon/soup_schema',
)
