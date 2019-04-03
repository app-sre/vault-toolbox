from setuptools import find_packages
from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='vault-toolbox',
    version='0.0.0',
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'vault-toolbox  = vault_toolbox.cli:cli',
        ],
    },
)
