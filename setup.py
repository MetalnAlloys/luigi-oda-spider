#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='luigi-oda-spider',
    version='0.0.1',
    description='Task trigger for Crawling Oda products',
    long_description=''' ''',
    long_description_content_type="text/markdown",
    author='Ali Humayun',
    author_email='ali.scmenust@gmail.com',
    url='https://github.com/',
    packages=setuptools.find_packages(),
    install_requires=[
        "luigi",
        "pyyaml",
        "requests",
        "beautifulsoup4"
   #     "google-auth",
    #    "google-api-python-client",
    ],
)
