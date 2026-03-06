# Makefile for common project tasks

.PHONY: train api dashboard eval setup all

setup:
	python -m venv venv
	. venv/bin/activate 2>/dev/null || . venv/Scripts/activate
	pip install --upgrade pip
	pip install -r requirements.txt

train:
	python run.py

eval:
	python src/evaluate_model.py

api:
	uvicorn api.pricing_api:app --reload

dashboard:
	streamlit run dashboard/app.py

all: setup train eval
