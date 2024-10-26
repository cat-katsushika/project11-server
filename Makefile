.PHONY: dev-build
dev-build:
	docker compose -f compose-dev.yml build

.PHONY: dev-up-d
dev-up-d:
	docker compose -f compose-dev.yml up -d

.PHONY: dev
dev:
	@make dev-build
	@make dev-up-d

.PHONY: down
down:
	docker compose -f compose-dev.yml down

.PHONY: bash
bash:
	docker compose -f compose-dev.yml exec django bash

.PHONY: logs
logs:
	docker compose -f compose-dev.yml logs

.PHONY: test
test:
	docker compose -f compose-dev.yml exec django python manage.py test

# pythonコードのリント
.PHONY: ruff-check
ruff-check:
	docker compose -f compose-dev.yml exec django ruff check --fix .

# pythonコードのフォーマット
.PHONY: ruff-format
ruff-format:
	docker compose -f compose-dev.yml exec django ruff format .

# pythonコードのフォーマットとリント
.PHONY: ruff
ruff:
	@make ruff-check
	@make ruff-format



## 以下、本番環境用
.PHONY: prod-build
prod-build:
	docker compose -f compose-prod.yml build

.PHONY: prod-up-d
prod-up-d:
	docker compose -f compose-prod.yml up -d

.PHONY: prod
prod:
	@make prod-build
	@make prod-up-d
