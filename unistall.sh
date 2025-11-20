#!/bin/bash

# Script de désinstallation de Nginx et Apache sur Debian
# Exécuter en tant que root: sudo bash uninstall_web_servers.sh

set -e

echo "================================================"
echo "Désinstallation Nginx et Apache"
echo "================================================"

echo ""
echo "🛑 Arrêt des services..."
systemctl stop nginx 2>/dev/null || true
systemctl stop apache2 2>/dev/null || true
systemctl stop gunicorn-mef_biblio_web 2>/dev/null || true

echo ""
echo "🗑️  Désinstallation de Nginx..."
if dpkg -l | grep -q nginx; then
    apt remove --purge -y nginx nginx-common nginx-full
    rm -rf /etc/nginx
    rm -rf /var/log/nginx
    rm -rf /var/lib/nginx
    echo "✓ Nginx désinstallé"
else
    echo "✓ Nginx n'est pas installé"
fi

echo ""
echo "🗑️  Désinstallation d'Apache..."
if dpkg -l | grep -q apache2; then
    apt remove --purge -y apache2 apache2-utils apache2-data
    rm -rf /etc/apache2
    rm -rf /var/log/apache2
    rm -rf /var/www/html
    echo "✓ Apache désinstallé"
else
    echo "✓ Apache n'est pas installé"
fi

echo ""
echo "🗑️  Nettoyage des services systemd..."
systemctl disable nginx 2>/dev/null || true
systemctl disable apache2 2>/dev/null || true
systemctl disable gunicorn-mef_biblio_web 2>/dev/null || true

rm -f /etc/systemd/system/gunicorn-mef_biblio_web.service
rm -f /etc/systemd/system/multi-user.target.wants/gunicorn-mef_biblio_web.service

echo ""
echo "🗑️  Suppression des configurations..."
rm -f /etc/nginx/sites-available/mef_biblio_web
rm -f /etc/nginx/sites-enabled/mef_biblio_web
rm -f /etc/apache2/sites-available/mef_biblio_web.conf
rm -f /etc/apache2/sites-enabled/mef_biblio_web.conf

echo ""
echo "🧹 Nettoyage des paquets..."
apt autoremove -y
apt autoclean

echo ""
echo "🔄 Rechargement du daemon systemd..."
systemctl daemon-reload

echo ""
echo "📊 Vérification de l'état des services..."
echo "Services actifs :"
systemctl list-units --type=service --state=running | grep -E "(nginx|apache|gunicorn)" || echo "Aucun service web actif"

echo ""
echo "================================================"
echo "✅ Désinstallation terminée avec succès !"
echo "================================================"
echo ""
echo "📋 Résultat :"
echo "   - ❌ Nginx désinstallé"
echo "   - ❌ Apache désinstallé" 
echo "   - ❌ Services Gunicorn supprimés"
echo "   - 🧹 Système nettoyé"
echo ""
echo "🌐 Votre application Django reste accessible via:"
echo "   http://localhost:8000 (si Gunicorn seul)"
echo "   ou python manage.py runserver"
echo "================================================"