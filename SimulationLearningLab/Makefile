.PHONY: dev test docker-build docker-run

dev:
	python run.py

test:
	pytest -q

docker-build:
	docker build -t simulation-learning-lab .

docker-run:
	docker run --rm -p 8787:8787 --env-file .env -v $$(pwd)/data:/app/data simulation-learning-lab
