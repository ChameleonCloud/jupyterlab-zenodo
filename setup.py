"""
Setup module for the jupyterlab_zenodo extension
"""

import pathlib
from setuptools import setup, find_packages
from jupyterlab_zenodo._version import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup_args = dict(
    name             = 'jupyterlab_zenodo',
    description      = 'A Jupyter Notebook extension which enables uploading to Zenodo from JupyterLab',
    version          = __version__,
    author           = 'University of Chicago',
    author_email     = 'dev@chameleoncloud.org',
    url              = 'https://github.com/chameleoncloud/jupyterlab-zenodo',
    license          = 'BSD',
    platforms        = 'Linux, Mac OS X, Windows',
    keywords         = ['jupyter', 'jupyterlab', 'openstack', 'zenodo'],
    long_description = README,
    classifiers      = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    packages         = find_packages(),
    data_files       = [
        ('etc/jupyter/jupyter_notebook_config.d', [
            'jupyter-config/jupyter_notebook_config.d/jupyterlab_zenodo.json'
        ]),
    ],
    zip_safe         = False,
    install_requires = [
        'notebook>=4.3.0',
        'python-slugify>=3.0.3',
    ],
    include_package_data = True,
    long_description_content_type = "text/markdown",
)

if __name__ == '__main__':
    setup(**setup_args)
