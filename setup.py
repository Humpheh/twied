from distutils.core import setup

setup(
    name="twied",
    version="0.2.4",
    description="Twitter event detection toolkit.",
    author="Humphrey Shotton",
    author_email="me@humpheh.com",
    url="https://github.com/Humpheh/twied",
    packages=[
        "twied",
        "twied.eventec",
        "twied.labelprop",
        "twied.multiind",
        "twied.multiind.indicators",
        "twied.multiind.interfaces",
        "twied.twicol"
    ],
    package_dir={
        'twied': 'src/twied',
        'twied.eventec': 'src/twied/eventec',
        'twied.labelprop': 'src/twied/labelprop',
        'twied.multiind': 'src/twied/multiind',
        'twied.multiind.indicators': 'src/twied/multiind/indicators',
        'twied.multiind.interfaces': 'src/twied/multiind/interfaces',
        'twied.twicol': 'src/twied/twicol',
    }
)
