pip freeze > requirements.txt
pip install -r ./requirements.txt

cd #app

set FLASK_APP=app.py
set FLASK_ENV=delevop
set FLASK_DEBUG=1

flask run

cd ..