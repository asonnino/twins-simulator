import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name='Streamlet Sim',
    author='Facebook, inc',
    description='A simpy simulation of streamlet tested with Twins.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/novifinancial',
    packages=setuptools.find_packages(where='streamlet'),
    package_dir={'': 'streamlet'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=required,
    version='0.0.1.dev1',
)
