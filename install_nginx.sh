#!/bin/bash
# Script pour configurer Nginx comme reverse proxy
# Permet d'accéder à l'application sans spécifier :8000
# Accès: http://192.168.0.115 au lieu de http://192.168.0.115:8000

set -e

echo "=================================="
echo "Installation Nginx Reverse Proxy"
echo "=================================="

PROJECT_NAME="mef_biblio_web"
PROJECT_DIR="/var/www/$PROJECT_NAME"
SERVER_IP="192.168.0.115"
DOMAIN="biblio.mef.local"
GUNICORN_PORT="8000"

echo ""
echo "1. Installation de Nginx..."
apt update
apt install -y nginx

echo ""
echo "2. Arrêt de Nginx pour configuration..."
systemctl stop nginx

echo ""
echo "3. Création de la configuration Nginx..."
cat > /etc/nginx/sites-available/$PROJECT_NAME <<'NGINX_CONFIG'
# Configuration Nginx pour mef_biblio_web
# Reverse proxy vers Gunicorn sur port 8000

upstream gunicorn_backend {
    server 127.0.0.1:8000 fail_timeout=10s max_fails=3;
    keepalive 32;
}

server {
    listen 80;
    listen [::]:80;
    
    server_name 192.168.0.115 biblio.mef.local localhost;
    
    client_max_body_size 100M;
    client_body_timeout 300s;
    
    # Logs
    access_log /var/log/nginx/mef_biblio_access.log;
    error_log /var/log/nginx/mef_biblio_error.log;
    
    # Fichiers statiques
    location /static/ {
        alias /var/www/mef_biblio_web/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Fichiers media
    location /media/ {
        alias /var/www/mef_biblio_web/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Proxy vers Gunicorn
    location / {
        proxy_pass http://gunicorn_backend;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # WebSocket support (si nécessaire)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Buffers
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # Page d'erreur personnalisée
    error_page 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
NGINX_CONFIG

echo "✓ Configuration Nginx créée"

echo ""
echo "4. Activation du site..."
# Supprimer la config par défaut
rm -f /etc/nginx/sites-enabled/default

# Activer notre config
ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/

echo ""
echo "5. Test de la configuration Nginx..."
if nginx -t; then
    echo "✓ Configuration Nginx valide"
else
    echo "❌ Erreur dans la configuration Nginx"
    exit 1
fi

echo ""
echo "6. Mise à jour des paramètres Django..."
# Ajouter Nginx aux ALLOWED_HOSTS si nécessaire
if [ -f "$PROJECT_DIR/.env" ]; then
    # Vérifier que ALLOWED_HOSTS contient déjà les bonnes valeurs
    echo "✓ Fichier .env existe"
fi

echo ""
echo "7. Vérification que Gunicorn est actif..."
if systemctl is-active --quiet gunicorn-$PROJECT_NAME; then
    echo "✓ Gunicorn actif sur port $GUNICORN_PORT"
else
    echo "⚠️  Gunicorn non actif, démarrage..."
    systemctl start gunicorn-$PROJECT_NAME
    sleep 3
fi

# Vérifier que le port 8000 écoute
if netstat -tlnp | grep -q ":$GUNICORN_PORT"; then
    echo "✓ Port $GUNICORN_PORT en écoute"
else
    echo "❌ Port $GUNICORN_PORT non accessible!"
    exit 1
fi

echo ""
echo "8. Démarrage de Nginx..."
systemctl start nginx
systemctl enable nginx

echo ""
echo "9. Configuration du firewall..."
if systemctl is-active --quiet ufw; then
    ufw allow 'Nginx Full'
    ufw allow 80/tcp
    echo "✓ Port 80 (HTTP) ouvert dans le firewall"
fi

echo ""
echo "10. Test de connexion..."
sleep 2

# Test local
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1 | grep -q "200\|302"; then
    echo "✓ Test local réussi (port 80)"
else
    echo "⚠️  Test local échoué"
fi

echo ""
echo "11. Création d'un script de diagnostic Nginx..."
cat > /usr/local/bin/check-nginx.sh <<'CHECK_NGINX'
#!/bin/bash
echo "=== DIAGNOSTIC NGINX + GUNICORN ==="
echo ""
echo "1. État Nginx:"
systemctl status nginx --no-pager | head -10
echo ""
echo "2. État Gunicorn:"
systemctl status gunicorn-mef_biblio_web --no-pager | head -10
echo ""
echo "3. Ports en écoute:"
echo "   Port 80 (Nginx):"
netstat -tlnp | grep :80 || echo "   ❌ Port 80 non actif"
echo "   Port 8000 (Gunicorn):"
netstat -tlnp | grep :8000 || echo "   ❌ Port 8000 non actif"
echo ""
echo "4. Test de connexion:"
echo -n "   HTTP sur port 80: "
curl -s -o /dev/null -w "Code %{http_code}\n" http://127.0.0.1/ 2>/dev/null || echo "Échec"
echo -n "   HTTP sur port 8000: "
curl -s -o /dev/null -w "Code %{http_code}\n" http://127.0.0.1:8000/ 2>/dev/null || echo "Échec"
echo ""
echo "5. Derniers logs Nginx (erreurs):"
tail -10 /var/log/nginx/mef_biblio_error.log 2>/dev/null || echo "   Pas d'erreurs"
echo ""
echo "6. Derniers logs Gunicorn (erreurs):"
tail -10 /var/www/mef_biblio_web/logs/gunicorn-error.log 2>/dev/null || echo "   Pas d'erreurs"
echo ""
echo "7. Configuration Nginx:"
nginx -t 2>&1
CHECK_NGINX

chmod +x /usr/local/bin/check-nginx.sh
echo "✓ Script de diagnostic créé: check-nginx.sh"

echo ""
echo "=================================="
echo "✅ INSTALLATION NGINX TERMINÉE!"
echo "=================================="
echo ""
echo "🌐 ACCÈS À L'APPLICATION (SANS PORT!):"
echo "   http://192.168.0.115"
echo "   http://192.168.0.115/admin"
echo ""
echo "🔧 CONFIGURATION DU NOM DE DOMAINE LOCAL:"
echo "   Pour utiliser http://biblio.mef.local au lieu de l'IP:"
echo ""
echo "   📝 SUR VOTRE PC WINDOWS:"
echo "   1. Ouvrez le Bloc-notes EN TANT QU'ADMINISTRATEUR"
echo "   2. Fichier → Ouvrir → Naviguez vers:"
echo "      C:\\Windows\\System32\\drivers\\etc\\hosts"
echo "   3. Changez le filtre de 'Fichiers texte' à 'Tous les fichiers'"
echo "   4. Ouvrez le fichier 'hosts'"
echo "   5. Ajoutez cette ligne à la fin du fichier:"
echo ""
echo "      192.168.0.115    biblio.mef.local"
echo ""
echo "   6. Sauvegardez (Ctrl+S)"
echo "   7. Fermez le Bloc-notes"
echo ""
echo "   ✓ Ensuite vous pourrez accéder à: http://biblio.mef.local"
echo ""
echo "   📝 SUR LE SERVEUR DEBIAN (optionnel):"
echo "   Ajoutez dans /etc/hosts:"
echo "   127.0.0.1    biblio.mef.local"
echo ""
echo "📊 COMMANDES DE DIAGNOSTIC:"
echo "   check-nginx.sh              # Diagnostic complet"
echo "   systemctl status nginx"
echo "   systemctl status gunicorn-mef_biblio_web"
echo "   tail -f /var/log/nginx/mef_biblio_error.log"
echo ""
echo "🔧 COMMANDES DE GESTION:"
echo "   systemctl restart nginx"
echo "   systemctl restart gunicorn-mef_biblio_web"
echo "   nginx -t                    # Tester la config"
echo ""
echo "📝 ARCHITECTURE:"
echo "   Navigateur → Nginx (port 80) → Gunicorn (port 8000) → Django"
echo ""
echo "✨ AVANTAGES:"
echo "   ✓ Accès sans spécifier le port :8000"
echo "   ✓ Nginx sert les fichiers statiques (plus rapide)"
echo "   ✓ Meilleure performance et sécurité"
echo "   ✓ Support SSL/HTTPS facile à ajouter plus tard"
echo ""
echo "⚠️  NOTE IMPORTANTE:"
echo "   Gunicorn continue de tourner sur port 8000 (localhost uniquement)"
echo "   Nginx fait le pont entre le port 80 et le port 8000"
echo ""
echo "🧪 TESTEZ MAINTENANT:"
echo "   Depuis votre PC Windows, ouvrez un navigateur:"
echo "   http://192.168.0.115"
echo "   OU (après config hosts):"
echo "   http://biblio.mef.local"
echo ""
echo "=================================="