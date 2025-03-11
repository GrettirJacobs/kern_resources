from setuptools import setup, find_packages

setup(
    name='kern_resources',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pytest'
    ]
)
