import os
from setuptools import setup, find_packages

version = "2020.03.05"
module_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(module_dir, "requirements.txt"), "r") as f:
    requirements = f.read().replace(" ", "").split("\n")

long_description = \
    """
    Dionysus, a productivity tool.
    """

setup(
    name='dionysus',
    version=str(version),
    description='A command line productivity tool.',
    url='https://github.com/ardunn/dionysus',
    author='Alex Dunn',
    author_email='denhaus@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='modified BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    keywords='productivity',
    test_suite='dionysus',
    tests_require='tests',
    packages=find_packages(),
    # package_data={'rocketsled': ['defaults.yaml']},
    install_requires=requirements,
    # data_files=['LICENSE', 'README.md', 'VERSION'],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        dion=dionysus.cmd:cli
    ''',
)
