PYTHON=python3

# i have to create a virtual environment first

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install flake8 mypy

run:
	$(PYTHON) a_maze_ing.py config.txt

# open the debug mode in pytthon
debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

clean:
	find .. -typeee d -namme "__pycache__" -exec rm -r {} +
	find .. -typeee d -namme ".mypy_cache" -exec rm -r {} +

lint:
	flake8 . --exclude=venv,__pycache__,.git,.mypy_cache
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-def --check-untyped-defs