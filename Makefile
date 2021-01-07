linux-graphviz: ; apt-get update && apt-get -qq -y install graphviz

init: ; pip install -r requirements.txt

unittest: ; python -m unittest discover -s ./tests/ -p '*test*.py'

test: ; coverage run -m unittest discover -s ./tests/ -p '*test*.py'