.PHONY: pyreverse

pyreverse:
	pyreverse \
	 -o png \
	 --source-roots src \
	 --output-directory class_diagram \
	 --colorized \
	 --ignore tests \
	 --only-classnames \
	 src
