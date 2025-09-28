.PHONY: tests migrate run pretty build up down

tests:
	@poetry run pytest --cov --cov-report html -n 4

migrate:
	@poetry run python manage.py migrate

run:
	@dbus-launch --exit-with-session poetry run python manage.py runserver

pretty:
	@poetry run black . && poetry run isort .
