JUPYTERLAB_ZENODO_SERVER_VERSION = $(shell cat VERSION)

.PHONY: publish-server
publish-server:
	python setup.py sdist
	twine upload dist/jupyterlab_zenodo-$(JUPYTERLAB_ZENODO_SERVER_VERSION).tar.gz

.PHONY: publish-client
publish-client:
	npm run-script build
	npm publish

.PHONY: tests
tests:
	python3 -m unittest discover jupyterlab_zenodo.tests
