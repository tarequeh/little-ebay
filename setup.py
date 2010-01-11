import os
from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name='little-ebay',
    version=version,
    description='Minimal auction system',
    author='Tareque Hossain',
    author_email='tareque@codexm.com',
    url='http://github.com/tarequeh/little-ebay/',
    packages=find_packages(),
    zip_safe=False,
    platforms=["any"],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
    )
