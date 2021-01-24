from distutils.core import setup

import setuptools

setup(
    name="shopper_invoicing_integration",
    version="0.dev4.1",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data = {
        '': ['templates/*.html'],
        'templates': ['*.html'],
    },
    license="",
    long_description=open("README.md").read(),
    install_requires=[
        "Flask==1.1.2",
        "pytest==6.1.1",
        "requests==2.21.0",
        "six==1.15.0",
        "Flask-Caching==1.8",
        "sentry-sdk==0.14.0",
        "arrow==0.15.5",
        "xhtml2pdf==0.2.5",
        "Flask-Email==1.4.4",
    ],
)
