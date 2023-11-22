DC = docker compose
APP_FILE = docker-compose/app.yml
DB_FILE = docker-compose/db.yml
RABBIT_FILE = docker-compose/rabbit.yml

.PHONY: app
app:
	${DC} -f ${APP_FILE} up -d

.PHONY: drop-app
drop-app:
	${DC} -f ${APP_FILE} down

.PHONY: all
all:
	${DC} -f ${APP_FILE} -f ${DB_FILE} -f ${RABBIT_FILE} up -d

.PHONY: drop-all
drop-all:
	${DC} -f ${APP_FILE} -f ${DB_FILE} -f ${RABBIT_FILE} down	

.PHONY: db
db:
	${DC} -f ${DB_FILE} up -d

.PHONY: drop-db
drop-db:
	${DC} -f ${DB_FILE} down

.PHONY: rabbit
rabbit:
	${DC} -f ${RABBIT_FILE} up -d

.PHONY: drop-rabbit
drop-rabbit:
	${DC} -f ${RABBIT_FILE} down