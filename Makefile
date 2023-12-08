# Package the project for distribution

all: clean package

clean:
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./TradingHaven.spec

package:
	pyinstaller \
		--name TradingHaven \
		--paths=C:/Users/Admin/.pyenv/versions/venv-haven \
		--hidden-import api_routes \
		server.py
	cp ./config-default.json ./dist/TradingHaven\_internal/config.json

config:
	cp ./config.json ./dist/TradingHaven\_internal/config.json

run:
	./dist/TradingHaven/TradingHaven

dev:
	python server.py

venv:
	C:/Users/Admin/.pyenv/versions/venv-haven/Scripts/activate
