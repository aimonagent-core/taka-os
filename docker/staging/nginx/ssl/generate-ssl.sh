#!/bin/bash
set -e

SSL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEY_FILE="$SSL_DIR/taka.key"
CRT_FILE="$SSL_DIR/taka.crt"

if [ -f "$KEY_FILE" ] && [ -f "$CRT_FILE" ]; then
    echo "Certificats SSL deja presents."
    exit 0
fi

echo "Generation du certificat SSL auto-signé pour staging..."

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CRT_FILE" \
    -subj "/C=FR/ST=Ile-de-France/L=Paris/O=TAKA OS/OU=Staging/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:0.0.0.0"

chmod 600 "$KEY_FILE"
chmod 644 "$CRT_FILE"

echo "Certificat genere :"
echo "  Cle : $KEY_FILE"
echo "  Cert : $CRT_FILE"
echo ""
echo "⚠️  Ce certificat est AUTO-SIGNE. Le navigateur affichera un avertissement."
echo "   En production, remplacer par Let's Encrypt :"
echo "   certbot certonly --standalone -d votre-domaine.com"
