#!/bin/bash

# Script de déploiement pour mef_biblio_web sur Debian 12
# Utilisation de Gunicorn SEUL sans Nginx
# Exécuter en tant que root: sudo bash deploy.sh

set -e  # Arrêter en cas d'erreur

echo "=================================="
echo "Déploiement de MEF Biblio Web - Gunicorn seul"
echo "=================================="

# Variables de configuration
PROJECT_NAME="mef_biblio_web"
PROJECT_DIR="/var/www/$PROJECT_NAME"
REPO_URL="https://github.com/louvinx/mef_biblio_web.git"
DOMAIN_OR_IP="biblio.mef.local"
APP_USER="www-data"
VENV_DIR="$PROJECT_DIR/venv"
SERVER_IP="192.168.0.100"
PORT="8000"  # Port pour Gunicorn

# Informations base de données
DB_NAME="mef_biblio"
DB_USER="root"
DB_PASSWORD="mefddne2025!"
DB_HOST="localhost"

echo ""
echo "1. Installation des dépendances système..."
if dpkg -l | grep -q python3-venv; then
    echo "✓ Dépendances déjà installées"
else
    apt update
    apt install -y python3 python3-pip python3-venv python3-dev \
        build-essential libmariadb-dev pkg-config git
fi

echo ""
echo "2. Création du répertoire du projet..."
mkdir -p $PROJECT_DIR

echo ""
echo "3. Clonage du dépôt Git..."
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "✓ Dépôt existant, mise à jour..."
    cd $PROJECT_DIR
    git pull
else
    cd /var/www
    if [ "$(ls -A $PROJECT_DIR)" ]; then
        echo "⚠️  Le répertoire n'est pas vide, suppression..."
        rm -rf $PROJECT_DIR/*
    fi
    git clone $REPO_URL $PROJECT_DIR
    echo "✓ Dépôt cloné"
fi

cd $PROJECT_DIR

echo ""
echo "4. Configuration de l'environnement virtuel Python..."
if [ -d "$VENV_DIR" ]; then
    echo "✓ Environnement virtuel existe déjà"
else
    python3 -m venv $VENV_DIR
    echo "✓ Environnement virtuel créé"
fi
source $VENV_DIR/bin/activate

echo ""
echo "5. Installation des dépendances Python..."
pip install --upgrade pip
pip install mysqlclient gunicorn
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Dépendances Python installées"
else
    echo "⚠️  Fichier requirements.txt introuvable"
fi

echo ""
echo "6. Vérification de la base de données MariaDB..."
if mysql -u $DB_USER -p$DB_PASSWORD -e "USE $DB_NAME; SHOW TABLES;" > /dev/null 2>&1; then
    echo "✓ Connexion à la base de données réussie"
else
    echo "❌ Erreur: Impossible de se connecter à la base de données"
    exit 1
fi

echo ""
echo "7. Création du fichier .env..."
cat > $PROJECT_DIR/.env <<ENV_FILE
SECRET_KEY='django-production-$(openssl rand -base64 32)'
DEBUG=False
ALLOWED_HOSTS=$DOMAIN_OR_IP,localhost,127.0.0.1,$SERVER_IP,192.168.0.100

DB_ENGINE=django.db.backends.mysql
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=$DB_HOST
DB_PORT=3306
ENV_FILE
echo "✓ Fichier .env créé"

echo ""
echo "8. Configuration des paramètres de production..."
mkdir -p $PROJECT_DIR/mef_biblio_web
cat > $PROJECT_DIR/mef_biblio_web/settings_prod.py <<'SETTINGS'
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

LOGIN_REDIRECT_URL = '/'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap4',
    'django_cleanup.apps.CleanupConfig',
    'biblio',
    'corsheaders',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mef_biblio_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'biblio.context_processors.global_stats',
            ],
        },
    },
]

WSGI_APPLICATION = 'mef_biblio_web.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'America/Port-au-Prince'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# IMPORTANT: Pour Gunicorn seul, désactiver la compression WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:$PORT",
    "http://127.0.0.1:$PORT",
    "http://$SERVER_IP:$PORT",
    "http://biblio.mef.local:$PORT",
]
SETTINGS
echo "✓ Fichier settings_prod.py créé"

echo ""
echo "9. Mise à jour de manage.py pour utiliser settings_prod..."
if [ -f "$PROJECT_DIR/manage.py" ]; then
    sed -i "s/mef_biblio_web.settings/mef_biblio_web.settings_prod/g" $PROJECT_DIR/manage.py
    echo "✓ manage.py mis à jour"
fi


if [ -f "$PROJECT_DIR/mef_biblio_web/wsgi.py" ]; then
    sed -i "s/mef_biblio_web.settings/mef_biblio_web.settings_prod/g" $PROJECT_DIR/mef_biblio_web/wsgi.py
    echo "✓ wsgi.py mis à jour pour utiliser settings_prod"
fi

echo ""
echo "10. Migrations de la base de données..."
source $VENV_DIR/bin/activate
python manage.py migrate
echo "✓ Migrations appliquées"

echo ""
echo "11. Collecte des fichiers statiques..."
python manage.py collectstatic --noinput
echo "✓ Fichiers statiques collectés"

echo ""
echo "12. Création d'un superutilisateur..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell
echo "✓ Superutilisateur vérifié/créé"

echo ""
echo "13. Configuration des permissions..."
chown -R $APP_USER:$APP_USER $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
mkdir -p $PROJECT_DIR/media $PROJECT_DIR/staticfiles
chmod -R 775 $PROJECT_DIR/media
echo "✓ Permissions configurées"

echo ""
echo "14. Configuration du service systemd pour Gunicorn..."
cat > /etc/systemd/system/gunicorn-$PROJECT_NAME.service <<GUNICORN_SERVICE
[Unit]
Description=Gunicorn daemon for $PROJECT_NAME
After=network.target

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn \\
    --workers 3 \\
    --bind 0.0.0.0:$PORT \\
    --timeout 120 \\
    --access-logfile $PROJECT_DIR/gunicorn-access.log \\
    --error-logfile $PROJECT_DIR/gunicorn-error.log \\
    mef_biblio_web.wsgi:application

[Install]
WantedBy=multi-user.target
GUNICORN_SERVICE
echo "✓ Service Gunicorn configuré"

echo ""
echo "15. Démarrage de Gunicorn..."
systemctl daemon-reload
systemctl start gunicorn-$PROJECT_NAME
systemctl enable gunicorn-$PROJECT_NAME
echo "✓ Gunicorn démarré et activé"

echo ""
echo "16. Configuration du firewall (si actif)..."
if systemctl is-active --quiet ufw; then
    ufw allow $PORT/tcp
    echo "✓ Port $PORT ouvert dans le firewall"
fi

echo "17. Configuration DNS local (optionnel)..."
echo ""
echo "📝 Pour utiliser le nom de domaine biblio.mef.local, ajoutez cette ligne"
echo "   dans le fichier /etc/hosts de VOTRE machine Windows :"
echo ""
echo "   192.168.0.100    biblio.mef.local"
echo ""
echo "🌐 Ensuite accédez à : http://biblio.mef.local:$PORT"

echo ""
echo "=================================="
echo "✅ Déploiement Gunicorn seul terminé !"
echo "=================================="
echo ""
echo "🌐 Accès à l'application:"
echo "   - Local: http://localhost:$PORT"
echo "   - Réseau: http://$SERVER_IP:$PORT"
echo "   - Admin: http://$SERVER_IP:$PORT/admin"
echo "   - User: admin / Password: admin123"
echo ""
echo "🔧 Commandes de gestion:"
echo "   - Status: systemctl status gunicorn-$PROJECT_NAME"
echo "   - Redémarrer: systemctl restart gunicorn-$PROJECT_NAME"
echo "   - Logs: journalctl -u gunicorn-$PROJECT_NAME -f"
echo "   - Logs détaillés: tail -f $PROJECT_DIR/gunicorn-error.log"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - Gunicorn seul gère aussi les fichiers statiques via WhiteNoise"
echo "   - Pour la production, envisagez Nginx plus tard pour de meilleures performances"
echo "   - Changez le mot de passe admin immédiatement"
echo "=================================="