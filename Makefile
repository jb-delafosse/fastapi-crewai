.PHONY: init venv package.upgrade requirements.txt requirements.upgrade format mypy start

VENV_PATH:=venv/bin
VENV:=source ${VENV_PATH}/activate
PY_VENV:=${VENV_PATH}/python3
PY_VENV_M:=${PY_VENV} -m
UVICORN_EXEC:= ${VENV_PATH}/uvicorn

PIP_COMPILE_EXEC:=piptools compile --quiet --generate-hashes --max-rounds=20 --upgrade
PRE_COMMIT_BIN:=${VENV_PATH}/pre-commit

venv/bin/python3.11:
	python3.11 -m venv venv

venv: venv/bin/python3.11
	${PY_VENV_M} pip install --quiet --upgrade pip 'pip-tools>=6.6.1'

init: venv
	${PY_VENV_M} piptools sync --pip-args '--no-deps' requirements.txt

requirements.txt: venv requirements.in
	${PY_VENV_M} $(PIP_COMPILE_EXEC) \
		--quiet --generate-hashes --max-rounds=20 \
		--output-file requirements.txt \
		requirements.in

requirements.upgrade:
	${PY_VENV_M} $(PIP_COMPILE_EXEC) \
		--quiet --generate-hashes --max-rounds=20 \
		--upgrade \
		--output-file requirements.txt \
		requirements.in

test:
	${PY_VENV_M} pytest .

format:
	${PY_VENV_M} black .
	${PY_VENV_M} isort .

mypy:
	${PY_VENV_M} mypy app/