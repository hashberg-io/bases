@echo off
mypy --strict bases
pylint bases
pytest test --cov=./bases
coverage html
@pause
