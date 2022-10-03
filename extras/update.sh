./start_maintenance.sh

cd app/
git pull origin master
poetry install
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
cd ..
./restart_app.sh

./end_maintenance.sh
