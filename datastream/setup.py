#!/usr/bin/env python

from setuptools import setup

setup(name='data-stream',
      version='0.1.0',
      install_requires=["requests >= 2.3.0",
                        "boto",
                        "python-dateutil"],
      description='Stream data from betadata services to THREDDs',
      author='Met Office Informatics Lab',
      maintainer='Met Office Informatics Lab',
      url='https://github.com/met-office-lab/data-stream',
      license='TBC',
      packages=['.'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
      ]
     )