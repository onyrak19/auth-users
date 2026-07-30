#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
extract_maj.py – Extrait le code source obfusqué depuis maj.py
Utilisation : python extract_maj.py
"""

import re
import zlib
import os
import sys

def extract_payload_and_salt(filename):
    """Lit le fichier et extrait payload_data et config_salt via regex."""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Recherche de payload_data = '...'
    payload_match = re.search(r"payload_data\s*=\s*'([^']*)'", content)
    if not payload_match:
        # Essayer avec guillemets doubles
        payload_match = re.search(r'payload_data\s*=\s*"([^"]*)"', content)
    if not payload_match:
        print(f"❌ Impossible de trouver payload_data dans {filename}")
        sys.exit(1)
    payload_hex = payload_match.group(1)

    # Recherche de config_salt = '...'
    salt_match = re.search(r"config_salt\s*=\s*'([^']*)'", content)
    if not salt_match:
        salt_match = re.search(r'config_salt\s*=\s*"([^"]*)"', content)
    if not salt_match:
        print(f"❌ Impossible de trouver config_salt dans {filename}")
        sys.exit(1)
    salt_hex = salt_match.group(1)

    return payload_hex, salt_hex

def decompress_payload(payload_hex, salt_hex):
    """Déchiffre et décompresse le payload."""
    b = bytes.fromhex(salt_hex)
    d = bytearray(a ^ b[i % len(b)] for i, a in enumerate(bytes.fromhex(payload_hex)))
    try:
        code = zlib.decompress(d).decode('utf-8')
        return code
    except Exception as e:
        print(f"❌ Erreur lors de la décompression : {e}")
        sys.exit(1)

def main():
    source_file = 'maj.py'
    if not os.path.exists(source_file):
        print(f"❌ Fichier {source_file} introuvable dans le répertoire courant.")
        sys.exit(1)

    print(f"📂 Extraction depuis {source_file}...")
    payload_hex, salt_hex = extract_payload_and_salt(source_file)
    print("✅ Payload et salt extraits avec succès.")

    code = decompress_payload(payload_hex, salt_hex)

    output_file = 'decompressed_maj.py'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"✅ Code décompressé sauvegardé dans {output_file}")

if __name__ == '__main__':
    main()
