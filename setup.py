# region Imports must have setuptools come first
from setuptools import setup, Extension
from Cython.Build import cythonize
from os import path
import numpy
# endregion

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

ext_options = {"language_level": 3}

setup(name='ParallelQueue', version='0.2', packages=['parallelqueue'],
      ext_modules=cythonize(["parallelqueue/*.pyx"], **ext_options), include_dirs=[numpy.get_include()],
      url='https://github.com/aarjaneiro/ParallelQueue', license='MIT', author='Aaron Janeiro Stone',
      author_email='ajstone@uwaterloo.ca', description='Parallel queueing models for SimPy',
      long_description=long_description, long_description_content_type='text/markdown')
