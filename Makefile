.PHONY: help install generate-data test run-local diagrams terraform-init clean

help:
	@echo "Available commands:"
	@echo "  make install        Install project dependencies"
	@echo "  make generate-data  Generate synthetic Ad Tech event streams"
	@echo "  make test           Run unit tests"
	@echo "  make run-local      Run end-to-end local pipeline simulation"
	@echo "  make diagrams       Generate high-resolution architecture diagrams"
	@echo "  make terraform-init Initialize Terraform GCP infrastructure"
	@echo "  make clean          Clean local temporary cache files"

install:
	pip install -r requirements.txt

generate-data:
	python scripts/generate_ad_data.py --impressions 25000 --days 90

test:
	python -m unittest discover tests

run-local:
	python scripts/run_local_pipeline.py

diagrams:
	python scripts/generate_diagrams.py

terraform-init:
	cd terraform && terraform init

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
