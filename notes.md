Needed for new versions of scikit-image / scipy:

`sudo apt-get install libatlas-base-dev libblas3 liblapack3 liblapack-dev libblas-dev gfortran`


For getting opengraph cards working:

`sudo apt-get install chromium-browser upower`


May also need to start server with a dbus session:

`$ dbus-launch --exit-with-session .venv/bin/python3 manage.py runserver` (on local)
