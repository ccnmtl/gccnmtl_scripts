bootstrap:
	python ./virtualenv.py --extra-search-dir requirements/virtualenv_support ve
	ve/bin/pip install --requirement requirements/requirements.txt

clean:
	rm -rf ve