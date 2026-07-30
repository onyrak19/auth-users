#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zlib
import os
import re
import random
import sys

def generate_salt(length=16):
    """Génère une clé hexadécimale aléatoire."""
    salt_bytes = bytes(random.randint(0, 255) for _ in range(length))
    return salt_bytes.hex()

def obfuscate(source_file, output_file):
    # 1. Lire le fichier source
    with open(source_file, 'r', encoding='utf-8') as f:
        source = f.read()

    # 2. Extraire la ligne ACCESS_CODE
    access_match = re.search(r'^(ACCESS_CODE\s*=\s*["\'].+?["\'])', source, re.MULTILINE)
    if not access_match:
        print("❌ Aucune ligne ACCESS_CODE trouvée dans le source.")
        sys.exit(1)
    access_line = access_match.group(1)

    # 3. Retirer cette ligne du source à obfusquer (pour éviter la duplication)
    source_without_access = source.replace(access_line, '', 1).lstrip()

    # 4. Compresser le reste
    compressed = zlib.compress(source_without_access.encode('utf-8'))

    # 5. Générer un salt
    salt_hex = generate_salt(16)
    salt_bytes = bytes.fromhex(salt_hex)

    # 6. XORer le payload
    payload_bytes = bytearray()
    for i, b in enumerate(compressed):
        payload_bytes.append(b ^ salt_bytes[i % len(salt_bytes)])
    payload_hex = payload_bytes.hex()

    # 7. Construire le fichier obfusqué
    obfuscated = f"""# -*- coding: utf-8 -*-
# Code d'accès requis par insta_kendou (en clair)
{access_line}

payload_data='{payload_hex}'
config_salt='{salt_hex}'

import zlib, base64
b = bytes.fromhex(config_salt)
d = bytearray(a ^ b[i % len(b)] for i, a in enumerate(bytes.fromhex(payload_data)))
exec(zlib.decompress(d).decode('utf-8'))
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(obfuscated)

    print(f"✅ Fichier obfusqué généré : {output_file}")
    print(f"   Salt utilisé : {salt_hex}")
    print("   Le code d'accès est conservé en clair pour permettre la validation.")

if __name__ == "__main__":
    source = "task_clear.py"      # votre script original en clair
    output = "task_obfuscated.py" # fichier obfusqué final

    if not os.path.exists(source):
        print(f"❌ Le fichier source '{source}' est introuvable.")
        print("   Veuillez le renommer ou modifier la variable 'source'.")
    else:
        obfuscate(source, output)
