#!/usr/bin/env bash
# Regenerate the WooCommerce outputs (wcpdf5164-*). Needs: PHP 8.2+ with mysqli, a MariaDB/MySQL
# server with an empty database, and network access to wordpress.org. Not run in CI.
# usage: DB_NAME=wp DB_USER=wp DB_PASS=wp DB_HOST=localhost generators/woocommerce/run.sh <corpus_dir> <out_dir> [site_dir]
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"; C="$(cd "$1" && pwd)"; mkdir -p "$2"; OUT="$(cd "$2" && pwd)"
SITE="${3:-$H/.site}"; mkdir -p "$SITE"; cd "$SITE"
dl() { curl -fsSL -o "$2" "$1"; echo "$3  $2" | sha256sum -c --quiet -; }
dl https://github.com/wp-cli/wp-cli/releases/download/v2.12.0/wp-cli-2.12.0.phar wp-cli.phar ce34ddd838f7351d6759068d09793f26755463b4a4610a5a5c0a97b68220d85c
WP="php $SITE/wp-cli.phar --path=$SITE/wp"
$WP core download --version=7.1.3 --locale=en_US --force
$WP config create --dbname="${DB_NAME:-wp}" --dbuser="${DB_USER:-wp}" --dbpass="${DB_PASS:-wp}" --dbhost="${DB_HOST:-localhost}" --force
$WP core install --url=http://localhost --title=conformance --admin_user=admin --admin_password=admin --admin_email=admin@example.invalid --skip-email
dl https://downloads.wordpress.org/plugin/woocommerce.11.2.1.zip woo.zip 5317434cb381b5fdc7c1dd6ee258324f08c390976aaf8d1199f2a0e9a3ab8586
dl https://downloads.wordpress.org/plugin/woocommerce-pdf-invoices-packing-slips.5.16.4.zip wcpdf.zip a23a0e17756294e119c88b63472ba4bf421bdb081d1ef1a7a883874eac086200
$WP plugin install woo.zip wcpdf.zip --activate --force
for SYN in ubl cii; do for RS in no yes; do
  N=300 SYN=$SYN ROUND_SUB=$RS OUT="$OUT" CARTS="$C/carts_b2b.json,$C/carts_b2c.json" $WP eval-file "$H/gen.php"
done; done
# gen_*.json files hold the platform's own order totals (see invoices/platform_order_totals.json)
