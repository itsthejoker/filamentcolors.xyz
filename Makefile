.PHONY: tests migrate run pretty build up down

tests:
	@poetry run pytest --cov --cov-report html -n 4

test_all:
	@poetry run pytest filamentcolors/tests --runplaywright

migrate:
	@poetry run python manage.py migrate

runwin:
	@dbus-launch --exit-with-session poetry run python manage.py runserver

run:
	poetry run python manage.py runserver

pretty:
	@poetry run black . && poetry run isort .
