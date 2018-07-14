#!/usr/bin/python3
# coding=utf-8

"""
Make ExpandCombinations an installable (by pip) package
"""

# from setuptools import setup
from distutils.core import setup

setup(
    name='expand-combinations',
    version='0.0.1',
    py_modules=['expand_combinations'],
    license='MIT',
    author='Phil Duby',
    summary='Generate multiple expanded dictionaries from nested dictionary and lists',
    # author_email='',
    url='https://github.com/mMerlin/expand_combos',
)
