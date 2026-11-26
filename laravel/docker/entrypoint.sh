#!/bin/sh
set -e

cd /var/www/html

echo "[entrypoint] fixing permissions..."
chown -R www-data:www-data storage bootstrap/cache || true
chmod -R ug+rwx storage bootstrap/cache || true

if [ ! -f vendor/autoload.php ]; then
  echo "[entrypoint] composer install..."
  composer install --no-interaction --prefer-dist --optimize-autoloader
  chown -R www-data:www-data vendor || true
fi

if [ ! -f .env ]; then
  cp .env.example .env
fi

# Ensure a single valid APP_KEY line (empty or corrupted keys break encryption)
if ! grep -qE '^APP_KEY=base64:[A-Za-z0-9+/=]+$' .env; then
  echo "[entrypoint] generating APP_KEY..."
  # strip any broken APP_KEY lines first
  sed -i '/^APP_KEY=/d' .env
  echo "APP_KEY=" >> .env
  php artisan key:generate --force
fi

php artisan config:clear || true
php artisan migrate --force || true

exec docker-php-entrypoint "$@"
