from setuptools import setup, find_packages


setup(
    name=f"victron-mqtt",
    description="Victron VE Direct to MQTT",
    python_requires = '>=3.8',
    use_scm_version={"root": ".", "relative_to": __file__},
    setup_requires=['setuptools_scm'],
    packages=find_packages(),
    include_package_data=True,
    entry_points = {
        'console_scripts': [f"victron-mqtt=victronmqtt.__main__:main"],
    },
    install_requires=[
        'paho-mqtt',
        'pyyaml',
        'vedirect @ git+https://github.com/karioja/vedirect'
    ]
)
