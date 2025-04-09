echo "Running black..."
poetry run black .
echo "Running djade..."
git ls-files -z -- '*.html' | xargs -0 poetry run djade --target-version 5.1
git ls-files -z -- '*.partial' | xargs -0 poetry run djade --target-version 5.1
