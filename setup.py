from setuptools import setup, find_packages

setup(
    name="amazfit_pyclient",
    version="0.1",  # Update with your project version
    packages=find_packages(
        exclude=["tests"],
    ),
    # include_package_data=False,
    install_requires=[
        "bleak",
        "cryptography",
    ],
    # Metadata
    author="MyrikLD",
    author_email="myrik260138@gmail.com",
    description="Amazfit Python Client",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MyrikLD/amazfit_pyclient",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    extras_require={
        "http": [
            "httpx",
            "yarl",
        ],
    },
    tests_setup="tests",
)
