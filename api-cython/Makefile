# Makefile for compiling Cython code

# Python version (modify if needed)
PYTHON_VERSION = 3.10

all: clean build run

clean:
	rm -rf ./dist
	rm -rf ./build

build:
	python$(PYTHON_VERSION) setup.py build_ext --build-lib=./dist

run:
	uvicorn --app-dir=./dist tradinghaven:app --reload
