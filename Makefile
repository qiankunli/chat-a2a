install:
	poetry install --no-root

install-test: WITH_GROUP = test
install-lint: WITH_GROUP = lint

install-%:
    # --no-root 不要安装 pyproject.toml 文件中定义的根依赖，而是直接根据 poetry.lock 文件安装依赖。
	poetry install --with $(WITH_GROUP)  --no-root

lint: install-lint
	poetry run ruff check --config .ruff.toml --fix --unsafe-fixes
	poetry run mypy --config-file=.mypy.ini .

install-with-pip:
	poetry install --no-interaction --no-ansi  --no-root

lint-ci: install-lint
	ruff check --config .ruff.toml --fix --unsafe-fixes
	mypy --config-file=.mypy.ini .

format:
	ruff format --check

exporter:
	poetry export -f requirements.txt --without-hashes --output requirements.txt

migration:
	python3 command.py migrate up

lock:
	poetry lock --no-update

test-ci: install-with-pip
	pip3 install --no-cache-dir -r requirements-test.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
		  --extra-index-url https://pypi.org/simple
	pytest tests/test_in_ci

