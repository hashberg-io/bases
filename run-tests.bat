@echo off
mypy --strict bases
pylint bases
python -m readme_renderer README.rst -o README-PROOF.html
pytest test --cov=./bases
coverage html
@pause
