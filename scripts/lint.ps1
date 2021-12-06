echo "`nRunning Pyright..."
pyright

echo "`nRunning Pylint..."
pylint --score=n --output-format=colorized $(git ls-files '**/*.py*')

echo "`nRunning Flake8..."
flake8

echo "`nRunning Bandit..."
bandit -f custom --silent --recursive src
