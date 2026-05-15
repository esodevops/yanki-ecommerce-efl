install:
	pip3 install -r requirements.txt

run-etl:
	python3 -m yanki_etl.main

run-etl-custom:
	python3 -m yanki_etl.main --raw-csv dataset/rawdata/yanki_ecommerce.csv --clean-dir dataset/cleandata

docker-build:
	docker build -t yanki-etl:latest .

docker-run:
	docker run --rm --env-file .env -v $(PWD)/dataset:/app/dataset yanki-etl:latest

compose-up:
	docker compose up --build etl

compose-down:
	docker compose down
