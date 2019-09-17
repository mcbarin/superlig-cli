from setuptools import setup

setup(
    name='superlig',
    version='0.4',
    py_modules=['superlig'],
    author="Mehmet Çağatay Barın",
    author_email="mcagataybarin@gmail.com",
    url="https://github.com/mcbarin/superlig-cli",
    description=("""Super Lig Client"""),
    install_requires=[
    'lxml',
    'click',
    'requests',
    'terminaltables',
    'beautifulsoup4'],
    entry_points='''
        [console_scripts]
        superlig=superlig:main
    '''
)

