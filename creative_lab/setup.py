from setuptools import setup, find_packages

setup(
    name="creative_lab",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "pytest",
        "pytest-cov"
    ],
)