from setuptools import setup, find_packages

setup(
    name="duck_db",
    version="0.1.0",
    packages=find_packages(),
    test_suite="tests",
    install_requires=[
        "duckdb == 1.0.0",
        "pandas == 2.2.2",
        "requests == 2.32.3",
        "pydantic == 2.8.2",
        "rich == 13.7.1",
        "boto3 == 1.34.151",
    ],
    entry_points={
        "console_scripts": [
            # If you have scripts to run, specify them here
        ],
    },
)
