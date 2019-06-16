from setuptools import setup
setup (
    name='snaptools',
    version='0.1',
    packages=['shotty'],
    url="https://github.com/harman76/snapshotalyzer-3100.git",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        cmd=shotty.shotty:cli
    ''',
)
