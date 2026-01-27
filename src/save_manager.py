import pickle
import os
import pygame
import traceback


# ═══════════════════════════════════════════════════════════════════════════════
# SAUVEGARDE : Sérialise l'état du jeu en retirant les objets Pygame non-sérialisables
# Sauvegarde les unités et la grille dans un fichier binaire pickle
# ═══════════════════════════════════════════════════════════════════════════════
def save_game_state(game, filename="quicksave.dat"):
    if not os.path.exists("saves"):
        os.makedirs("saves")
    
    filepath = os.path.join("saves", filename)
    
    stored_images = {}
    stored_frames = {}
    
    for unit in game.all_soldats:
        stored_images[unit] = unit.image
        unit.image = None
        
        if hasattr(unit, 'frames') and unit.frames:
            stored_frames[unit] = unit.frames
            unit.frames = []
        
        unit._class_name = unit.__class__.__name__

    data = {
        "units": list(game.all_soldats),
        "grid": game.grid
    }
    
    try:
        with open(filepath, "wb") as f:
            pickle.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        print(f"[*] Fichier MIS À JOUR avec succès : {filepath}")
    except Exception as e:
        print(f"[!] Erreur critique lors du F11 : {e}")
    finally:
        for unit, img in stored_images.items():
            unit.image = img
        for unit, frames in stored_frames.items():
            unit.frames = frames


# ═══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT : Restaure l'état du jeu et recharge les images depuis le disque
# Gère les spritesheets (Paladin bleu) et les images statiques
# ═══════════════════════════════════════════════════════════════════════════════
def load_game_state(game, filename="quicksave.dat"):
    filepath = os.path.join("saves", filename)
    if not os.path.exists(filepath):
        print("[!] Fichier de sauvegarde introuvable.")
        return False

    try:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        
        game.all_soldats.empty()
        for unit in data["units"]:
            class_name = getattr(unit, '_class_name', unit.__class__.__name__)
            # Recalculer les positions de grille
            gx = int(unit.rect.x // 32)
            gy = int(unit.rect.y // 32)

            # --- GESTION DES ANIMATIONS AU CHARGEMENT ---
            if class_name == "Halberdier":
                if unit.team == 1:
                    path = "./assets/PikemanRedWalk/Pikemanwalk"
                else:
                    path = "./assets/PikemanBleuWalk/Pikemanwalk"
                unit.frames = []
                unit.load_animation_frames(gx, gy, path)
                
            elif class_name == "Arbalester":
                if unit.team == 1:
                    path = "./assets/ArlebestRedWalk/Arlebestwalk"
                else:
                    path = "./assets/ArlebestBleuWalk/Arlebestwalk"
                unit.frames = []
                unit.load_animation_frames(gx, gy, path)
                
            elif class_name == "Paladin":
                if unit.team == 1:
                    path = "./assets/KnightRedWalk.png"
                else:
                    path = "./assets/KnightBleuWalk.png"
                unit.frames = []
                # Paladin utilise une méthode différente (_load_blue_spritesheet)
                unit._load_blue_spritesheet(gx, gy, path)
                
            elif unit.img_path:
                # Fallback pour les unités sans animation complexe
                original_img = pygame.image.load(unit.img_path)
                new_w = original_img.get_width() // 2
                new_h = original_img.get_height() // 2
                unit.image = pygame.transform.scale(original_img, (new_w, new_h))
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