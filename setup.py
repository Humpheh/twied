from distutils.core import setup

setup(name="twied",
      version="0.2",
      description="Twitter event detection toolkit.",
      author="Humphrey Shotton",
      author_email="me@humpheh.com",
      url="https://github.com/Humpheh/twied",
      packages=["twied"],
      package_dir={'twied': 'src/twied'}
)