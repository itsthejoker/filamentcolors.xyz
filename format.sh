echo "Running black..."
black .
echo "Running djade..."
git ls-files -z -- '*.html' | xargs -0 djade --target-version 5.1
git ls-files -z -- '*.partial' | xargs -0 djade --target-version 5.1