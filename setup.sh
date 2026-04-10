#!/bin/bash
set -e

echo "Checking dependencies..."
missing=()
for cmd in gh railway git python3; do
  command -v "$cmd" &>/dev/null || missing+=("$cmd")
done

if [ ${#missing[@]} -gt 0 ]; then
  echo "Missing required tools: ${missing[*]}"
  echo ""
  echo "Install instructions:"
  echo "  gh:      https://cli.github.com"
  echo "  railway: npm install -g @railway/cli"
  echo "  git:     https://git-scm.com"
  echo "  python3: https://python.org"
  exit 1
fi

echo "Available templates:"
for dir in templates/*/; do
  echo "  - $(basename "$dir")"
done

echo ""
echo "Setting up Python venv..."
cd bootstrap_service
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt

if [ ! -f .env ]; then
  cat > .env <<'EOF'
BOOTSTRAP_SECRET=
GITHUB_TOKEN=
GITHUB_DEFAULT_OWNER=
RAILWAY_API_TOKEN=
EOF
  echo "Created bootstrap_service/.env — fill in your credentials before running."
else
  echo "bootstrap_service/.env already exists, skipping."
fi

echo ""
echo "Done. To start the service:"
echo "  cd bootstrap_service && source .venv/bin/activate && uvicorn main:app --reload --port 8000"
