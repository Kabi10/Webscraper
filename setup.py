from setuptools import setup, find_packages

setup(
    name="webscraper",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "python-dotenv==1.0.0",
        "googlemaps==4.10.0"
    ],
) 