import requests
import json
import base64

# 🔑 Configuration (remplace par un nouveau token si tu as exposé l'ancien)
GITHUB_TOKEN = "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"  # ⚠️ À révoquer et regénérer ! 
OWNER = "onyrak19"
REPO = "auth-users"
FILE_PATH = "users.json"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_file_and_sha():
    """Récupère le contenu du fichier et son SHA."""
    response = requests.get(API_URL, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content), data["sha"]
    else:
        raise Exception(f"Erreur de lecture : {response.status_code}")

def update_file_on_github(new_content, commit_message):
    """Met à jour le fichier sur GitHub."""
    _, sha = get_file_and_sha()
    payload = {
        "message": commit_message,
        "content": base64.b64encode(json.dumps(new_content, indent=2).encode()).decode(),
        "sha": sha
    }
    response = requests.put(API_URL, headers=HEADERS, json=payload)
    if response.status_code in [200, 201]:
        print("✅ Mise à jour réussie.")
        return True
    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        return False

# ========== Fonctions CRUD ==========
def read_users():
    data, _ = get_file_and_sha()
    return data

def add_user(new_user):
    data, _ = get_file_and_sha()
    for user in data["users"]:
        if user["user_id"] == new_user["user_id"]:
            print(f"❌ L'utilisateur {new_user['user_id']} existe déjà.")
            return False
    data["users"].append(new_user)
    return update_file_on_github(data, f"Ajout de {new_user['user_id']}")

def update_user(user_id, updated_fields):
    data, _ = get_file_and_sha()
    for user in data["users"]:
        if user["user_id"] == user_id:
            user.update(updated_fields)
            return update_file_on_github(data, f"Mise à jour de {user_id}")
    print(f"❌ Utilisateur {user_id} introuvable.")
    return False

def delete_user(user_id):
    data, _ = get_file_and_sha()
    original_count = len(data["users"])
    data["users"] = [u for u in data["users"] if u["user_id"] != user_id]
    if len(data["users"]) == original_count:
        print(f"❌ Utilisateur {user_id} introuvable.")
        return False
    return update_file_on_github(data, f"Suppression de {user_id}")

# ========== Menu interactif ==========
def menu():
    print("\n" + "="*40)
    print("  GESTION DES UTILISATEURS - GitHub")
    print("="*40)
    print("1. Afficher tous les utilisateurs")
    print("2. Ajouter un utilisateur")
    print("3. Modifier le statut d'un utilisateur")
    print("4. Supprimer un utilisateur")
    print("5. Quitter")
    print("="*40)

if __name__ == "__main__":
    while True:
        menu()
        choix = input("Votre choix (1-5) : ").strip()

        if choix == "1":
            data = read_users()
            print("\n📋 Liste des utilisateurs :")
            print(json.dumps(data, indent=2))

        elif choix == "2":
            print("\n--- Ajout d'un nouvel utilisateur ---")
            api_id = input("api_id : ").strip()
            api_hash = input("api_hash : ").strip()
            phone = input("phone_number (ex: +261...) : ").strip()
            user_id = input("user_id : ").strip()
            status = input("status (active/inactive) [défaut active] : ").strip() or "active"
            new_user = {
                "api_id": api_id,
                "api_hash": api_hash,
                "phone_number": phone,
                "user_id": user_id,
                "status": status
            }
            add_user(new_user)

        elif choix == "3":
            print("\n--- Modification du statut ---")
            user_id = input("user_id de l'utilisateur à modifier : ").strip()
            new_status = input("Nouveau statut (active/inactive) : ").strip()
            if new_status not in ("active", "inactive"):
                print("❌ Statut invalide. Utilise 'active' ou 'inactive'.")
            else:
                update_user(user_id, {"status": new_status})

        elif choix == "4":
            print("\n--- Suppression d'un utilisateur ---")
            user_id = input("user_id à supprimer : ").strip()
            confirm = input(f"Confirmer la suppression de '{user_id}' ? (o/n) : ").strip().lower()
            if confirm == "o":
                delete_user(user_id)
            else:
                print("Annulé.")

        elif choix == "5":
            print("👋 Au revoir !")
            break

        else:
            print("❌ Choix invalide, veuillez entrer un nombre entre 1 et 5.")
