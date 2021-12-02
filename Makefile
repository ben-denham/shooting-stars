meteor-deps:
	docker-compose run --rm meteor npm install
meteor-bash:
	docker-compose run --rm meteor /bin/bash

deps: meteor-deps

run:
	docker-compose up
