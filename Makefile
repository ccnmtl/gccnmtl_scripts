bootstrap:
	python ./virtualenv.py --extra-search-dir requirements/virtualenv_support ve
	ve/bin/pip install --requirement requirements/requirements.txt

clean-creds:
	rm ~/.credentials/calendar-python-quickstart.json
	rm ~/.credentials/calendar-python-gccnmtl-calendars.json

clean:
	rm ~/.credentials/calendar-python-quickstart.json
	rm ~/.credentials/calendar-python-gccnmtl-calendars.json
	rm -rf ve