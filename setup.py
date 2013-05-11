#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='megacl',
      version='0.4.5',
      description='mega.co.nz command line client.',
      author='Arthibus Gisséhel',
      author_email='public-dev-megacl@gissehel.org',
      url='https://github.com/gissehel/megacl.git',
      packages=['megacllib'],
      scripts=['mcl','megacl'],
      license='MIT',
      keywords='commandline mega.co.nz mega',
      long_description=open('README.rst').read(),
      install_requires=['supertools','cltools>=0.4.0','mega.py>=0.9.10',
        'requests', # non declared yet mega.py dependency
        'pycrypto', # non declared yet mega.py dependency
        ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Topic :: Communications',
          'Topic :: Internet',
          'Topic :: System :: Filesystems',
          'Topic :: Utilities',
      ],
)
