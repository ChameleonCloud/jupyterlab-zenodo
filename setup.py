"""
Setup module for the jupyterlab_zenodo proxy extension
"""
from setuptools import setup, find_packages

setup_args = dict(
    name             = 'jupyterlab_zenodo',
    description      = 'A Jupyter Notebook server extension which acts a proxy for a Swift API.',
    version          = '0.0.1',
    author           = 'University of Chicago',
    author_email     = 'dev@chameleoncloud.org',
    url              = 'https://www.chameleoncloud.org',
    license          = 'BSD',
    platforms        = 'Linux, Mac OS X, Windows',
    keywords         = ['jupyter', 'jupyterlab', 'zenodo'],
    classifiers      = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    packages = find_packages(),
    include_package_data = True,
    data_files = [
        ('etc/jupyter/jupyter_notebook_config.d', [
            'jupyter-config/jupyter_notebook_config.d/jupyterlab_zenodo.json'
        ]),
    ],
    zip_safe = False,
    install_requires = [
        'notebook>=4.3.0',
    ]
)

if __name__ == '__main__':
    setup(**setup_args)
