import setuptools

from osu_cleaner_cli import __desc__, __version__


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="osu_cleaner_cli",
    version=__version__,
    py_modules=["osu_cleaner_cli"],
    author="Layerex",
    author_email="layerex@dismail.de",
    description=__desc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Layerex/osu-cleaner-cli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 6 - Mature",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "osu-cleaner-cli = osu_cleaner_cli:main",
        ],
    },
)
