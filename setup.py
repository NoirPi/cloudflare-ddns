import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="cloudflare-ddns",
    version="1.0.1",
    author="NoirPi",
    description="Script to dynamically update multiple cloudflare records on one zonefile with your actual ip",
    keywords="ddns dyndns cloudflare automation",
    packages=["ddns"],
    install_requires=["aiohttp>=3.7.4"],
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/NoirPi/cloudflare-ddns",
    entry_points=dict(
        console_scripts='ddns=ddns:main'
    )
)
