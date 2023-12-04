# Package the project for distribution

all: clean package run

clean:
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./TradingHaven.spec

package:
	pyinstaller --name TradingHaven --paths=~/.pyenv/versions/venv-haven --hidden-import tradinghaven packager.py

run:
	./dist/TradingHaven
