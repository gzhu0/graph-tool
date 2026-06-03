run:
	uvicorn src.main:app --reload

dev:
	uvicorn app.main:app --reload