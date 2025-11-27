echo ""
echo "Correction des fichiers statiques..."
cd $PROJECT_DIR
source $VENV_DIR/bin/activate

# Réinitialiser les fichiers statiques
echo "Suppression du dossier staticfiles..."
rm -rf staticfiles/
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Vérifier
echo "Vérification de la présence du logo..."
if [ -f "staticfiles/logo.png" ]; then
    echo "✓ Logo trouvé dans staticfiles/"
else
    echo "❌ Logo non trouvé, copie manuelle..."
    mkdir -p staticfiles/
    cp media/logo.png staticfiles/logo.png 2>/dev/null || echo "Logo non disponible"
fi

# Configuration des permissions
echo "Configuration des permissions..."
chown -R www-data:www-data staticfiles/
chmod -R 755 staticfiles/
chmod 644 staticfiles/logo.png 2>/dev/null || echo "Fichier logo non présent"

# Vérification des permissions
echo "Vérification des permissions..."
ls -la staticfiles/ | head -5

# Redémarrer Gunicorn pour appliquer les changements WhiteNoise
echo "Redémarrage de Gunicorn..."
systemctl restart gunicorn-mef_biblio_web
echo "✓ Gunicorn redémarré pour appliquer la configuration WhiteNoise"