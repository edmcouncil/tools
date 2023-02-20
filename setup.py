from setuptools import setup
from setuptools import find_packages

setup(
    name='EDMC tools',
    version='0.1',
    description='EDMC Python tools',
    url='https://github.com/edmcouncil/tools',
    author='Pawel Garbacz',
    author_email='pgarbacz@edmcouncil.com',
    license='MIT',
    python_requires='>=3.8.8',
    packages=find_packages(),
    # package_dir={'': 'tools'},
    install_requires=
    [
        'rdflib',
        'PyGithub',
        'networkx',
        'matplotlib',
        'tqdm',
        'spacy',
        'nltk',
        'pandas',
        'requests',
        'openpyxl',
        'wikibase_api',
        'ply',
        'pyshacl',
        'owlready2',
        'openai',
        'Github',
        'pyjsonviewer',
        'gitpython',
        'PyYAML',
        'xlsxwriter'
    ],
    entry_points={
        'console_scripts':
            [
            'github_compare=compare.run_github_compare:run',
            'folder_compare=compare.run_local_compare:run',
            ],
    },
    zip_safe=False
)