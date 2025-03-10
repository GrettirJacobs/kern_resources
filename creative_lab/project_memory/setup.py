from setuptools import setup, find_packages

setup(
    name="project_memory",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask>=3.0.0',
        'python-dotenv>=1.0.0',
        'transformers>=4.36.2',
        'torch>=2.1.2',
        'nltk>=3.8.1',
        'markdown>=3.5.1',
        'python-dateutil>=2.8.2',
        'sentence-transformers>=2.5.1',
        'textblob>=0.17.1',
        'networkx>=3.2.1',
        'plotly>=5.18.0',
        'numpy>=1.17',
        'scikit-learn>=1.0.0',
    ],
)
