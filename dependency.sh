#!/bin/bash

# System Dependencies Installation Script for mef_biblio_web

echo "=========================================="
echo "System Dependencies Installation"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check root privileges
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root: sudo $0"
    exit 1
fi

info "Updating packages..."
apt update
apt upgrade -y

info "Installing main system dependencies..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libmariadb-dev \
    pkg-config \
    git \
    curl \
    wget

info "Installing image processing dependencies..."
apt install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev

info "Installing MariaDB if not present..."
if ! command -v mysql &> /dev/null; then
    warn "MariaDB not found, installing..."
    apt install -y mariadb-server mariadb-client
    systemctl start mariadb
    systemctl enable mariadb
else
    info "✓ MariaDB already installed"
fi


info "Verifying installations..."
echo "Python3: $(python3 --version)"
echo "Pip: $(pip3 --version)"
echo "Git: $(git --version)"
echo "MySQL: $(mysql --version 2>/dev/null || echo 'Not installed')"

info "Creating www-data user if needed..."
if ! id "www-data" &>/dev/null; then
    useradd -r -s /bin/false www-data
    info "✓ www-data user created"
else
    info "✓ www-data user already exists"
fi

echo ""
echo "=========================================="
echo "✅ System dependencies installed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run your deployment script"
echo "2. Verify database configuration"
echo "3. Test the application"
echo ""
echo "Test commands:"
echo "python3 --version"
echo "pip3 --version"
echo "mysql --version"
echo "systemctl status mariadb"
echo "=========================================="