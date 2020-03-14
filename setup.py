import setuptools

from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setuptools.setup(
    name="cryptocompare_loading", # Replace with your own username
    version="0.0.1",
    author="janFi",
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    author_email="jphdsn@gmail.com",
    description="A package to download cryptocompare flux in postgresql",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #packages=['cryptocompare_loading'],
    include_package_data=True,
    platforms='any',
    test_suite='cryptocompare_loading.test.cryptocompare_loading',
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    licence="MIT",
    platform="any",
    extras_require={'testing': ['pytest'],
    }
)
