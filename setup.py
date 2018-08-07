import unittest

from setuptools import setup


def readme():
    with open('README.rst', mode='r') as f:
        return f.read()


def test_suite():
    loader = unittest.TestLoader()
    return loader.discover('tests', pattern='test_*.py')


setup(
    name='call',
    version='0.1',
    packages=['call'],
    url='',
    license='MIT',
    author='Nathan Graule',
    author_email='solarliner@gmail.com',
    description='Thread-based, JS-like asynchronous calls for Python.',
    long_description=readme(),
    test_suite='setup.test_suite'
)
