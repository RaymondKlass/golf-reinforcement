from setuptools import setup

app_config = {
    'name': "golf",
    'version': "0.0.1",
    'author': "Raymond Klass",
    'author_email': "raymond.klass@gmail.com",
    'description': "Golf Card Game Model",
    'packages': ["golf"],
    'include_package_data': True,
    'zip_safe': False,
    'install_requires': [
        "mock==1.0.1",
        "nose==1.3.7",
        "numpy==1.12.*",
        "unittest2==1.1.0",

    ],
    'url': "https://github.com/RaymondKlass/golf-reinforcement"
}

setup(**app_config)