#!/usr/bin/env bash
set -euo pipefail

# ── Detect OS ──────────────────────────────────────────────────────────────────

OS="$(uname -s)"
case "$OS" in
  Darwin) PLATFORM="mac" ;;
  Linux)  PLATFORM="linux" ;;
  *)      echo "Unsupported OS: $OS"; exit 1 ;;
esac

# ── Helpers ────────────────────────────────────────────────────────────────────

info()    { echo "[·] $*"; }
success() { echo "[✓] $*"; }
warn()    { echo "[!] $*"; }
die()     { echo "[✗] $*" >&2; exit 1; }

has() { command -v "$1" &>/dev/null; }

install_mac() {
  local pkg=$1
  if ! has brew; then
    die "Homebrew not found. Install it from https://brew.sh then re-run."
  fi
  info "Installing $pkg via Homebrew..."
  brew install "$pkg"
}

install_linux() {
  local pkg=$1
  if has apt-get; then
    info "Installing $pkg via apt..."
    sudo apt-get install -y "$pkg"
  elif has dnf; then
    info "Installing $pkg via dnf..."
    sudo dnf install -y "$pkg"
  elif has yum; then
    info "Installing $pkg via yum..."
    sudo yum install -y "$pkg"
  else
    die "No supported package manager found. Install $pkg manually."
  fi
}

install() {
  [ "$PLATFORM" = "mac" ] && install_mac "$1" || install_linux "$1"
}

# ── Dependencies ───────────────────────────────────────────────────────────────

echo ""
info "Checking dependencies..."

# python3
if ! has python3; then
  [ "$PLATFORM" = "mac" ] && install python3 || install python3
fi
success "python3 $(python3 --version 2>&1 | awk '{print $2}')"

# git
if ! has git; then
  install git
fi
success "git $(git --version | awk '{print $3}')"

# gh (GitHub CLI)
if ! has gh; then
  if [ "$PLATFORM" = "mac" ]; then
    install gh
  else
    info "Installing GitHub CLI..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
      | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
      | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt-get update && sudo apt-get install -y gh
  fi
fi
success "gh $(gh --version | head -1 | awk '{print $3}')"


# ── Python venv ────────────────────────────────────────────────────────────────

echo ""
info "Setting up Python venv..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/bootstrap_service"

python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
success "Python dependencies installed"

# ── .env ──────────────────────────────────────────────────────────────────────

echo ""
if [ ! -f .env ]; then
  cat > .env <<'EOF'
GITHUB_TOKEN=
RAILWAY_API_TOKEN=      # from railway.app → Account Settings → Tokens (workspace-scoped token works)
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_TEAM=
# GITHUB_DEFAULT_OWNER=  # optional: defaults to authenticated GitHub user
EOF
  success "Created bootstrap_service/.env — fill in your credentials before running."
else
  warn "bootstrap_service/.env already exists, skipping."
fi

# ── Templates ─────────────────────────────────────────────────────────────────

echo ""
info "Available templates:"
for dir in "$SCRIPT_DIR/templates"/*/; do
  echo "    - $(basename "$dir")"
done

# ── Done ──────────────────────────────────────────────────────────────────────

echo ""
success "Setup complete."
echo ""
echo "    See INIT.md for credentials you need to fill into bootstrap_service/.env"
echo ""
echo "    To start:"
echo "    cd bootstrap_service && source .venv/bin/activate && uvicorn main:app --reload --port 8000"
echo ""
