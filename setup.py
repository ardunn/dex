import os
from setuptools import setup, find_packages


version = "0.1.1.20200806"
module_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(module_dir, "requirements.txt"), "r") as f:
    requirements = f.read().replace(" ", "").split("\n")

long_description = \
    """
    Day executor - dex - organizing your days so you don't have to.
    """

setup(
    name='dex',
    version=str(version),
    description='A command line productivity tool.',
    url='https://github.com/ardunn/dex',
    author='Alex Dunn',
    author_email='denhaus@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='modified BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    keywords='productivity',
    test_suite='dex',
    tests_require='tests',
    packages=find_packages(),
    # package_data={'rocketsled': ['defaults.yaml']},
    install_requires=requirements,
    # data_files=['LICENSE', 'README.md', 'VERSION'],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        dex=dex.cmd:cli
    ''',
)
