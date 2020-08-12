import os
from setuptools import setup, find_packages


version = "0.1.2.20200810"
module_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(module_dir, "requirements.txt"), "r") as f:
    requirements = f.read().replace(" ", "").split("\n")

long_description = \
    """
    dex (day executor) - an ultra-minimal command line productivity tool.
    """

setup(
    name='dex',
    version=str(version),
    description='An ultra-minimal command line productivity tool.',
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
    data_files=['README.md', 'LICENSE'],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        dex=dex.cmd:cli
    ''',
)
