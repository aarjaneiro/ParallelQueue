from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='ParallelQueue', version='0.1.5.0', packages=['parallelqueue'],
      url='https://github.com/aarjaneiro/ParallelQueue', license='MIT', author='Aaron Janeiro Stone',
      author_email='ajstone@uwaterloo.ca', description='Parallel queueing models for SimPy',
      long_description=long_description, long_description_content_type='text/markdown')
