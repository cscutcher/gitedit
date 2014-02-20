from setuptools import setup, find_packages

setup_kwargs = {
    "name": "GitEdit",
    "version": "0.1",
    "packages":  find_packages(),
    "install_requires": ["pygit2", "klein"],
    "test_suite": "gitedit.tests.all_suite",
}

setup(**setup_kwargs)
