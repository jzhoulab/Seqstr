import sys
import os
from setuptools import setup

GENOME_DIR = None

for arg in sys.argv:
    if arg.startswith("--dir="):
        GENOME_DIR = arg.split("=")[1]
        break

if GENOME_DIR is None:
    GENOME_DIR = "./"

config_file_path = os.path.expanduser("~/.seqstr.config")
config_exists = os.path.isfile(config_file_path)

if not config_exists:
    open(config_file_path, "w").close()

with open(config_file_path, "w") as config_file:
    config_file.write(f"GENOME_DIR={GENOME_DIR}")

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name='seqstr',
    version='0.0.8',
    packages=['seqstr'],
    install_requires=[
        'requests',
        'pyfaidx',
    ],
    entry_points = {
        'console_scripts': [
            'CLI_seqstr = seqstr.seqstr:main',
        ]
    },
    author="Chenlai Shi",              
    author_email="shichenlai@gmail.com",  
    maintainer="Chenlai Shi",          
    maintainer_email="shichenlai@gmail.com",  
    url="https://github.com/jzhoulab/Seqstr/",  
    long_description=long_description, 
    long_description_content_type="text/markdown",  
    license="MIT",
)
