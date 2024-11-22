bash:
	docker compose exec $(service) /bin/bash
run-bash:
	docker compose run --rm $(service) /bin/bash
sudo-bash:
	docker compose exec -u root $(service) /bin/bash
sudo-run-bash:
	docker compose run --rm -u root $(service) /bin/bash

web-deps:
	docker compose run --rm web npm install
web-mongo:
	docker compose exec web /home/node/.meteor/meteor mongo
web-reset-db:
	docker compose exec web /home/node/.meteor/meteor reset --db

controller-deps:
	docker compose run --rm controller-lights python -m pip install --user -r requirements.txt

deps: web-deps controller-deps

dev-deps:
	docker compose run --rm controller-lights python -m pip install --user -r dev-requirements.txt

run:
	docker compose up
jupyter:
	docker compose up jupyter
