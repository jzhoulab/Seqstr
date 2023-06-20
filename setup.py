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

config_file_path = "~/.seqstr.config"
config_exists = os.path.isfile(config_file_path)

if not config_exists:
    open(config_file_path, "w").close()

with open(config_file_path, "w") as config_file:
    config_file.write(f"GENOME_DIR={GENOME_DIR}")


setup(
    name='seqstr',
    version='1.0',
    packages=['seqstr'],
    install_requires=[
        'requests',
        'selene_sdk',
    ],
)
