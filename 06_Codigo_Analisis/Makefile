PYTHON ?= python

.PHONY: audit catalog derived validate yolo folds grid test all

audit:
	$(PYTHON) scripts/10_audit_sources.py

catalog:
	$(PYTHON) scripts/11_build_page_catalog.py

derived:
	$(PYTHON) scripts/12_build_derived_480.py --overwrite

validate:
	$(PYTHON) scripts/13_validate_derived_480.py

yolo:
	$(PYTHON) scripts/14_convert_yolo.py

folds:
	$(PYTHON) scripts/15_build_folds.py

grid:
	$(PYTHON) scripts/16_make_condition_grid.py

test:
	$(PYTHON) -m pytest -q

all: audit catalog derived validate yolo folds grid test
