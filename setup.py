from setuptools import setup

# Explicitly configure for single module package
setup(
    name='superlig',
    version='1.1.0',
    description='Terminal client that gives info about Turkish Football League (Süper Lig)',
    author='Mehmet Çağatay Barın',
    author_email='mcagataybarin@gmail.com',
    url='https://github.com/mcbarin/superlig-cli',
    py_modules=['superlig'],
    python_requires='>=3.10',
    install_requires=[
        'click>=8.0',
        'requests>=2.31.0',
        'rich>=13.0.0',
        'beautifulsoup4>=4.12.0',
        'lxml>=4.9.0',
    ],
    entry_points={
        'console_scripts': [
            'superlig=superlig:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Utilities',
    ],
)
