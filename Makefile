DC=docker compose -f infra/docker/docker-compose.yml

up:
	$(DC) up --build

down:
	$(DC) down

