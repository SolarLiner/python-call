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
    url='https://gitlab.com/solarliner/call',
    license='MIT',
    author='Nathan Graule',
    author_email='solarliner@gmail.com',
    description='Thread-based, JS-like asynchronous calls for Python.',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='setup.test_suite'
)
