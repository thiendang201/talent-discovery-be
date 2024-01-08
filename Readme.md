generate requirements: pip3 freeze > requirements.tx

# Setup

## For the first time

1. python -m venv env
2. env\Scripts\activate
3. pip install -r requirements.txt
4. uvicorn main:app --reload

## Run

1. ativate env: env/Scripts/activate
2. run: uvicorn main:app --reload
