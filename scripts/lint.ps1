pylint --score=n --output-format=text,colorized $(git ls-files '**/*.py*')
# pylint --reports=y --output-format=text,colorized $(git ls-files '**/*.py*')
mypy .
# mypy --pretty src
pyright
bandit -f custom --silent --severity-level medium -r .
# bandit -n 1 --severity-level medium -r src
flake8
