""" setup.py created according to https://packaging.python.org/tutorials/packaging-projects """

import setuptools #type:ignore

with open("README.md", "r") as fh:
    long_description: str = fh.read()

setuptools.setup(
    name="bases",
    version="0.1.0",
    author="hashberg",
    author_email="sg495@users.noreply.github.com",
    url="https://github.com/hashberg-io/bases",
    description="Python library for general Base-N encodings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["test"]),
    classifiers=[ # see https://pypi.org/classifiers/
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
    package_data={"": [],
                  "bases": ["bases/py.typed"],
                 },
    install_requires=[
        "typing_extensions"
    ],
    extras_require={
        "dev": [
            "mypy",
            "pylint",
            "pytest",
            "pytest-cov",
            "base58"
        ]
    },
    include_package_data=True
)
