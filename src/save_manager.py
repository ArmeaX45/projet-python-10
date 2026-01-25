import pickle
import os
import pygame
import traceback

def save_game_state(game, filename="quicksave.dat"):
    if not os.path.exists("saves"):
        os.makedirs("saves")
    
    filepath = os.path.join("saves", filename)
    
    # Étape 1 : On prépare les données en retirant TOUT ce qui est Pygame (images/surfaces)
    stored_images = {}
    stored_frames = {}
    
    for unit in game.all_soldats:
        # Stocker l'image actuelle
        stored_images[unit] = unit.image
        unit.image = None
        
        # Stocker les frames d'animation si elles existent
        if hasattr(unit, 'frames') and unit.frames:
            stored_frames[unit] = unit.frames
            unit.frames = []
        
        # Ajouter le nom de la classe pour la reconstruction
        unit._class_name = unit.__class__.__name__

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
        # Étape 3 : On rend les images et frames au jeu
        for unit, img in stored_images.items():
            unit.image = img
        for unit, frames in stored_frames.items():
            unit.frames = frames

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
            # Recharger l'image selon le type d'unité
            class_name = getattr(unit, '_class_name', unit.__class__.__name__)
            
            # Si c'est un Paladin de l'équipe 0 (avec spritesheet)
            if class_name == "Paladin" and unit.team == 0:
                # Recharger le spritesheet
                unit.frames = []
                unit._load_blue_spritesheet(unit.rect.x // unit.rect.width, unit.rect.y // unit.rect.height)
            # Si c'est une unité avec un chemin d'image
            elif unit.img_path:
                original_img = pygame.image.load(unit.img_path)
                new_w = original_img.get_width() // 2
                new_h = original_img.get_height() // 2
                unit.image = pygame.transform.scale(original_img, (new_w, new_h))
            # Sinon, créer une image par défaut
            else:
                unit.image = pygame.Surface((32, 32), pygame.SRCALPHA)
                color = (50, 50, 200) if unit.team == 0 else (200, 50, 50)
                unit.image.fill(color)
            
            game.all_soldats.add(unit)
        
        game.grid = data["grid"]
        print("[*] Chargement TERMINE avec succès !")
        return True
    except Exception as e:
        print(f"[!] Erreur au chargement : {e}")
        traceback.print_exc()
        return False