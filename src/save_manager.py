import pickle
import os
import pygame

def save_game_state(game, filename="quicksave.dat"):
    if not os.path.exists("saves"):
        os.makedirs("saves")
    
    filepath = os.path.join("saves", filename)
    
    # Étape 1 : On prépare les données en retirant TOUT ce qui est Pygame (images/surfaces)
    stored_images = {}
    for unit in game.all_soldats:
        stored_images[unit] = unit.image
        unit.image = None 

    data = {
        "units": list(game.all_soldats),
        "grid": game.grid
    }
    
    try:
        # Étape 2 : On ouvre en mode 'wb' (écriture binaire), ce qui doit écraser l'ancien
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
            f.flush() # Force l'écriture sur le disque immédiatement
            os.fsync(f.fileno()) # Sécurité supplémentaire pour le système de fichiers
        print(f"[*] Fichier MIS À JOUR avec succès : {filepath}")
    except Exception as e:
        print(f"[!] Erreur critique lors du F11 : {e}")
    finally:
        # Étape 3 : On rend les images au jeu
        for unit, img in stored_images.items():
            unit.image = img

def load_game_state(game, filename="quicksave.dat"):
    """Charge l'état et recharge les images depuis le disque."""
    filepath = os.path.join("saves", filename)
    if not os.path.exists(filepath):
        print("[!] Fichier de sauvegarde introuvable.")
        return False

    try:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        
        game.all_soldats.empty()
        for unit in data["units"]:
            # On utilise le chemin enregistré pour recharger l'image PNG
            unit.image = pygame.image.load(unit.img_path).convert_alpha()
            game.all_soldats.add(unit)
        
        game.grid = data["grid"]
        print("[*] Chargement TERMINE avec succès !")
        return True
    except Exception as e:
        print(f"[!] Erreur au chargement : {e}")
        return False