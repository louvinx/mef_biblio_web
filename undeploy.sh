#!/bin/bash

# Script de nettoyage pour mef_biblio_web (sans toucher la base de données)
# Supprime tout sauf la base de données
# Exécuter en tant que root: sudo bash cleanup_deployment.sh

set -e

echo "================================================"
echo "NETTOYAGE - MEF Biblio Web (Base de données conservée)"
echo "================================================"

# Variables
PROJECT_NAME="mef_biblio_web"
PROJECT_DIR="/var/www/$PROJECT_NAME"
APP_USER="www-data"
VENV_DIR="$PROJECT_DIR/venv"
PORT="8000"

echo ""
echo "🛑 Arrêt des services..."
systemctl stop gunicorn-$PROJECT_NAME 2>/dev/null || true
systemctl disable gunicorn-$PROJECT_NAME 2>/dev/null || true

echo ""
echo "🗑️  Suppression du service systemd..."
rm -f /etc/systemd/system/gunicorn-$PROJECT_NAME.service
rm -f /etc/systemd/system/multi-user.target.wants/gunicorn-$PROJECT_NAME.service
systemctl daemon-reload
systemctl reset-failed

echo ""
echo "🗑️  Suppression du projet et des fichiers..."
if [ -d "$PROJECT_DIR" ]; then
    echo "Suppression de $PROJECT_DIR..."
    rm -rf $PROJECT_DIR
    echo "✓ Répertoire projet supprimé"
else
    echo "✓ Répertoire projet n'existe pas"
fi

echo ""
echo "🗑️  Suppression des règles firewall..."
if systemctl is-active --quiet ufw; then
    ufw delete allow $PORT/tcp 2>/dev/null || true
    echo "✓ Règle firewall supprimée"
fi

echo ""
echo "🔍 Vérification des processus restants..."
pkill -f "gunicorn.*$PROJECT_NAME" 2>/dev/null || true

echo ""
echo "📊 Nettoyage des logs..."
rm -f /var/log/gunicorn-* 2>/dev/null || true

echo ""
echo "================================================"
echo "✅ NETTOYAGE TERMINÉ AVEC SUCCÈS !"
echo "================================================"
echo ""
echo "📋 Ce qui a été supprimé :"
echo "   ❌ Service systemd: gunicorn-$PROJECT_NAME"
echo "   ❌ Répertoire projet: $PROJECT_DIR"
echo "   ❌ Règle firewall port $PORT"
echo "   ❌ Fichiers de logs Gunicorn"
echo ""
echo "📋 Ce qui est conservé :"
echo "   ✅ Base de données: mef_biblio (TOUTES LES DONNÉES)"
echo "   ✅ MariaDB/MySQL"
echo "   ✅ Python et paquets système"
echo "   ✅ Utilisateur $APP_USER"
echo ""
echo "🌐 Pour une réinstallation :"
echo "   La base de données et les données sont intactes"
echo "   Relancez le script de déployement pour réinstaller"
echo "================================================"