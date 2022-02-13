SHELL := /bin/bash

# system python interpreter. used only to create virtual environment
PY = python3
VENV = venv
BIN=$(VENV)/bin

# make it work on windows too
ifeq ($(OS), Windows_NT)
    BIN=$(VENV)/Scripts
    PY=python
endif

$(VENV): requirements.txt 
	$(PY) -m venv $(VENV)
	$(BIN)/pip3 install --upgrade -r requirements.txt

	touch $(VENV)

.PHONY: deploy-full
deploy-full: $(VENV)
	source venv/bin/activate; \
	export PATH=${HOME}/.pulumi/bin:${PATH};\
	export PULUMI_CONFIG_PASSPHRASE='';\
		pulumi login ${PULUMI_BUCKET}; \
		pulumi stack select ${PULUMI_STACK};
		pulumi up --yes --skip-preview

.PHONY: build
build: $(VENV)
	pip3 install -r requirements.txt