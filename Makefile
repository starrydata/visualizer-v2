.PHONY: pyreverse coverage

pyreverse:
	pyreverse \
	 -o png \
	 --source-roots src \
	 --output-directory class_diagram \
	 --colorized \
	 --ignore tests \
	 --only-classnames \
	 --all-associated --all-ancestors \
	 src

coverage:
	coverage run -m pytest && coverage report
