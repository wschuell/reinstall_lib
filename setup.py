#!/usr/bin/env python

import re
import sys

from setuptools import setup, find_packages


def version():
    with open('reinstall_lib/_version.py') as f:
        return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read()).group(1)

def requirements():
  with open('requirements.txt') as f:
    return f.readlines()

setup(name='reinstall_lib',
      version=version(),
      packages=['reinstall_lib'],#find_packages(),
      install_requires=[requirements()],
      author='',
      author_email='',
      description='',
      url='',
      license='GNU AFFERO GENERAL PUBLIC LICENSE Version 3',
      )
