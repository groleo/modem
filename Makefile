tests:
	PYTHONPATH=. python test/test-recv.py
#	PYTHONPATH=. python test/test-send.py
#	PYTHONPATH=. python test/test.py test/test.py

upload:
	python setup.py sdist upload
	python setup.py bdist_egg upload
	python setup.py build_sphinx upload_sphinx

