# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='FoodAdvisorBot',
    version='0.1.0',
    description='',
    long_description=readme,
    author='Sevastyan Rakhimov',
    author_email='rakhimov.se@gmail.com',
    url='https://github.com/RakhimovSE/FoodAdvisorBot',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

