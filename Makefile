# Package the project for distribution

all: clean package deploy

clean:
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./TradingHaven.spec

package:
	pyinstaller \
		--name TradingHaven \
		--paths=C:/Users/Admin/.pyenv/versions/venv-haven \
		--hidden-import api_routes \
		--icon=./stock.ico \
		server.py
	cp ./config-default.json ./dist/TradingHaven\_internal/config.json

deploy:
	rm -rf C:/TradingHaven/_internal/
	rm C:/TradingHaven/TradingHaven.exe
	cp -r ./dist/TradingHaven/_internal/ C:/TradingHaven/
	cp ./dist/TradingHaven/TradingHaven.exe C:/TradingHaven/
	cp C:/TradingHaven/config.json C:/TradingHaven/_internal/

config:
	cp ./config.json ./dist/TradingHaven\_internal/config.json

run:
	./dist/TradingHaven/TradingHaven

dev:
	python server.py

venv:
	C:/Users/Admin/.pyenv/versions/venv-haven/Scripts/activate
