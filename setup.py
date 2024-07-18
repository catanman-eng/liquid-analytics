from setuptools import setup, find_packages

setup(
    name="liquid_analytics",
    version="0.1.0",
    packages=find_packages(),
    test_suite="tests",
    install_requires=[
        "duckdb == 1.0.0"
    ],
    entry_points={
        "console_scripts": [
            # If you have scripts to run, specify them here
        ],
    },
)