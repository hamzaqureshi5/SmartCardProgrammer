from setuptools import setup

setup(
    name="SIM Programmer",
    version="1.0",
    packages=[],
    url="",
    license="",
    author_email="",
    description="Tools related to SIM/USIM cards",
    install_requires=[
        "pyscard",
        "serial",
        "pytlv",
        "cmd2 >= 1.5.0",
        "jsonpath-ng",
        "construct >= 2.9.51",
        "bidict",
        "gsm0338",
        "pyyaml >= 5.1",
        "termcolor",
        "colorlog",
        "pycryptodomex",
        "packaging",
    ],
    scripts=[],
)
