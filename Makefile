init: ; pip install -r requirements.txt

unittest: ; python -m unittest discover -s ./tests/ -p '*test*.py'

test: ; coverage run -m unittest discover -s ./tests/ -p '*test*.py'