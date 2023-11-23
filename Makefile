DC = docker compose
APP_FILE = docker-compose/app.yml
DB_FILE = docker-compose/db.yml
RABBIT_FILE = docker-compose/rabbit.yml

.PHONY: application
application:
	${DC} -f ${APP_FILE} -f ${DB_FILE} -f ${RABBIT_FILE} up -d

.PHONY: drop-application
drop-application:
	${DC} -f ${APP_FILE} -f ${DB_FILE} -f ${RABBIT_FILE} down	