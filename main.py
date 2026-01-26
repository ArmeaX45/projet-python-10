# main.py - Point d'entrée unifié pour la simulation de bataille
"""
Usage:
    python main.py                                      # Mode graphique interactif (défaut)
    python main.py run <AI1> <AI2> [-t] [-d DATAFILE]   # Lancer une bataille
    python main.py load <savefile>                      # Charger une sauvegarde
    python main.py tourney [-G AI1 AI2...] [-N 10] [-na] # Lancer un tournoi
"""

import argparse
import sys
import os
import time
import threading
import math

# ============================================================
#                   IMPORTS DES CLASSES EXISTANTES
# ============================================================
from src.map import Map
from src.game import Game
from src.ai_daft import MajorDaftSimple
from src.ia_braindead import GeneralBrainDead
from src.ColonelSMART import ColonelSMART
from src.save_manager import save_game_state, load_game_state
from src.stats_generator import check_end_and_report

# Imports des unités (pour le mode headless)
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester

# Dictionnaire des IAs disponibles
AI_REGISTRY = {
    "MajorDaftSimple": MajorDaftSimple,
    "MajorDaft": MajorDaftSimple,
    "DAFT": MajorDaftSimple,
    "GeneralBrainDead": GeneralBrainDead,
    "BrainDead": GeneralBrainDead,
    "BRAIN": GeneralBrainDead,
    "ColonelSMART": ColonelSMART,
    "SMART": ColonelSMART,
}

# Scénarios prédéfinis
def get_scenario_configs(name):
    """Retourne (config_0, config_1) pour un nom de scénario donné."""
    name = name.lower()
    
    if name == "standard":
        # 20 de chaque
        c = {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
        return c.copy(), c.copy()
        
    elif name == "small":
        # Petite escarmouche
        c = {"Halberdier": 5, "Paladin": 2, "Arbalester": 2}
        return c.copy(), c.copy()
        
    elif name == "duel":
        # 1 Paladin vs 1 Hallebardier
        return {"Paladin": 1}, {"Halberdier": 1}
        
    elif name == "archers":
        # Full distance
        c = {"Arbalester": 30}
        return c.copy(), c.copy()
        
    elif name == "horde":
        # Beaucoup de petits vs peu de gros
        return {"Halberdier": 50}, {"Paladin": 10, "Arbalester": 10}
        
    else:
        # Par défaut Standard
        print(f"[!] Scénario '{name}' inconnu. Utilisation de 'Standard'.")
        c = {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
        return c.copy(), c.copy()

def get_ai_class(name):
    """Récupère une classe IA par son nom."""
    if name in AI_REGISTRY:
        return AI_REGISTRY[name]
    raise ValueError(f"IA inconnue: {name}. Disponibles: {list(AI_REGISTRY.keys())}")


# ============================================================
#                   MODE HEADLESS (SANS PYGAME)
# ============================================================


# ============================================================
#                   MODE HEADLESS & CURSES
# ============================================================

class HeadlessGame:
    """Version headless du jeu pour les tournois rapides."""
    
    def __init__(self, width=60, height=34):
        self.width = width
        self.height = height
        self.all_soldats = []
        self.lock = threading.Lock()
    
    def add_soldat(self, soldat):
        self.all_soldats.append(soldat)
    
    def remove_soldat(self, soldat):
        if soldat in self.all_soldats:
            self.all_soldats.remove(soldat)

def _setup_headless_game(config_0, config_1, width=60, height=34):
    """Prépare une instance de HeadlessGame avec les soldats."""
    game = HeadlessGame(width=width, height=height)
    
    class_map = {
        "Halberdier": Halberdier,
        "Paladin": Paladin,
        "Arbalester": Arbalester
    }
    
    # Créer les soldats équipe 0 (gauche)
    start_x, start_y = 2, 5
    col = 0
    for unit_type, count in config_0.items():
        for i in range(count):
            soldat = class_map[unit_type](start_x + col, start_y + i, 0)
            game.add_soldat(soldat)
        col += 1
    
    # Créer les soldats équipe 1 (droite)
    start_x = game.width - 3
    col = 0
    for unit_type, count in config_1.items():
        for i in range(count):
            soldat = class_map[unit_type](start_x - col, start_y + i, 1)
            game.add_soldat(soldat)
        col += 1
        
    return game

def run_curses_battle(stdscr, config_0, config_1, ai1_class, ai2_class):
    """Exécute une bataille visualisée dans le terminal avec curses."""
    import curses
    import pygame  # Import nécessaire ici pour la fonction
    
    # MOCK PYGAME DISPLAY pour éviter les erreurs d'init spritesheet
    if not pygame.display.get_init():
        pygame.display.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    # Configuration Curses
    curses.curs_set(0) # Cacher le curseur
    stdscr.nodelay(True) # Non-bloquant
    stdscr.timeout(1)  # Rafraîchissement rapide (1ms d'attente)
    
    # Couleurs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK) # Equipe 0
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  # Equipe 1
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK) # UI
    
    # Initialisation Jeu
    game = _setup_headless_game(config_0, config_1)
    
    # IAs
    ia_0 = ai1_class(team_name=0)
    ia_1 = ai2_class(team_name=1)
    
    turn = 0
    paused = False
    
    # Vitesse : combien de tours logiques par rafraîchissement d'écran ?
    # Augmentez ce nombre pour que ça aille "plus vite" visuellement
    KEY_REPEAT = 5 
    
    while True:
        # -- Gestion Entrées --
        key = stdscr.getch()
        if key == ord('q'):
            return None # Quitter
        elif key == ord('p') or key == ord(' '):
            paused = not paused
        
        # -- Logique Jeu (Boucle accélérée) --
        # On calcule plusieurs tours de jeu AVANT d'afficher
        # Cela accélère considérablement le "temps de jeu"
        turns_to_process = KEY_REPEAT if not paused else 0
        
        # Si c'est la fin de partie, on force 1 tour pour détecter le gagnant
        alive_0 = [s for s in game.all_soldats if s.team == 0 and s.is_alive]
        alive_1 = [s for s in game.all_soldats if s.team == 1 and s.is_alive]
        
        winner = None
        if not alive_0 and not alive_1: winner = -1 
        elif not alive_0: winner = 1
        elif not alive_1: winner = 0
            
        if winner is not None:
             # Fin de partie détectée
            stdscr.addstr(game.height + 2, 0, f"FIN DE LA PARTIE ! Vainqueur: {'EQUIPE 1' if winner==1 else 'EQUIPE 0' if winner==0 else 'EGALITE'}", curses.A_BOLD)
            stdscr.addstr(game.height + 3, 0, "Appuyez sur 'q' pour quitter.", curses.A_BLINK)
            stdscr.refresh()
            stdscr.timeout(-1) # Bloquant
            while True:
                kp = stdscr.getch()
                if kp == ord('q'): return _get_result_dict(game, turn, winner, ai1_class, ai2_class, _get_initial_counts(config_0, config_1))

        # Boucle de simulation multiple
        for _ in range(turns_to_process):
            turn += 1
             # Obtenir les actions des IAs
            actions_0 = ia_0.update(game)
            actions_1 = ia_1.update(game)
            all_actions = actions_0 + actions_1
            
            # Exécuter les actions
            for action in all_actions:
                if action[0] == "move":
                    _, unit, dx, dy = action
                    if unit.is_alive:
                        unit.move(game, dx=dx, dy=dy)
                elif action[0] == "attack":
                    _, unit, target = action
                    if unit.is_alive and target.is_alive:
                        unit.attack(target)
            
            # Nettoyer les morts après chaque sous-tour
            game.all_soldats = [s for s in game.all_soldats if s.is_alive]
            
            # Vérifier victoire dans la sous-boucle pour s'arrêter net
            alive_0 = [s for s in game.all_soldats if s.team == 0 and s.is_alive]
            alive_1 = [s for s in game.all_soldats if s.team == 1 and s.is_alive]
            if not alive_0 or not alive_1:
                break
        
        # -- Affichage --
        try:
            stdscr.erase()
            
            # Dimensions actuelles du terminal
            max_y, max_x = stdscr.getmaxyx()
            
            # Info Header
            header1 = f"Tour: {turn} | {'PAUSE' if paused else 'EN COURS'} | (q: quitter, p: pause)"
            header2 = f"Bleus: {len(alive_0)} | Rouges: {len(alive_1)}"
            
            # Vérifier si on a la place d'afficher
            if max_y < game.height + 5 or max_x < game.width + 2:
                stdscr.addstr(0, 0, "Terminal trop petit !", curses.color_pair(3))
                stdscr.addstr(1, 0, f"Requis: {game.width+2}x{game.height+5}", curses.color_pair(3))
                stdscr.addstr(2, 0, f"Actuel: {max_x}x{max_y}", curses.color_pair(3))
                stdscr.refresh()
                continue
                
            stdscr.addstr(0, 0, header1[:max_x-1], curses.color_pair(3))
            stdscr.addstr(1, 0, header2[:max_x-1], curses.color_pair(3))
            
            # Dessin de la map
            offset_y = 3
            # Cadre
            stdscr.addstr(offset_y - 1, 0, "+" + "-"*game.width + "+")
            stdscr.addstr(offset_y + game.height, 0, "+" + "-"*game.width + "+")
            
            for y in range(game.height):
                stdscr.addch(offset_y + y, 0, "|")
                try:
                    stdscr.addch(offset_y + y, game.width + 1, "|")
                except: pass # Ignorer si ça dépasse à l'extrême droite
                
            # Unités
            # Construire une grille simple pour l'affichage
            display_grid = {}
            for s in game.all_soldats:
                gx, gy = int(s.rect.x // 32), int(s.rect.y // 32)
                if 0 <= gx < game.width and 0 <= gy < game.height:
                    display_grid[(gx, gy)] = s
            
            for y in range(game.height):
                for x in range(game.width):
                    # Coordonnées écran
                    scr_y = offset_y + y
                    scr_x = x + 1
                    
                    if 0 <= scr_y < max_y and 0 <= scr_x < max_x:
                        if (x, y) in display_grid:
                            s = display_grid[(x, y)]
                            char = s.tag # H, A, P
                            color = curses.color_pair(1) if s.team == 0 else curses.color_pair(2)
                            try:
                                stdscr.addch(scr_y, scr_x, char, color)
                            except: pass 
                        else:
                            try:
                                stdscr.addch(scr_y, scr_x, ".")
                            except: pass

            stdscr.refresh()
        except curses.error:
            pass # Ignorer les erreurs de dessin (redimensionnement fenêtre, etc)

def _get_initial_counts(c0, c1):
    return {0: sum(c0.values()), 1: sum(c1.values())}

def _get_result_dict(game, turn, winner, ai1, ai2, initial_counts):
    # Résultats finaux pour rapport
    remaining_0 = len([s for s in game.all_soldats if s.team == 0 and s.is_alive])
    remaining_1 = len([s for s in game.all_soldats if s.team == 1 and s.is_alive])
    hp_total_0 = sum(s.hp for s in game.all_soldats if s.team == 0 and s.is_alive)
    hp_total_1 = sum(s.hp for s in game.all_soldats if s.team == 1 and s.is_alive)
    
    return {
        "winner": winner,
        "turns": turn,
        "initial_counts": initial_counts,
        "remaining_counts": {0: remaining_0, 1: remaining_1},
        "remaining_hp": {0: hp_total_0, 1: hp_total_1},
        "ai1": ai1.__name__,
        "ai2": ai2.__name__,
    }

def run_headless_battle(config_0, config_1, ai1_class, ai2_class, max_turns=10000, width=60, height=34):
    """
    Exécute une bataille en mode 100% headless (rapide, sans affichage).
    Utilisé pour les tournois.
    """
    import pygame  # Import nécessaire pour le mock display
    
    # MOCK PYGAME DISPLAY pour éviter les erreurs d'init
    if not pygame.display.get_init():
        pygame.display.init()
        # Créer une surface factice cachée si possible, ou juste init
    if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.HIDDEN)
            
    game = _setup_headless_game(config_0, config_1, width=width, height=height)
    initial_counts = _get_initial_counts(config_0, config_1)

    
    # Créer les IAs
    ia_0 = ai1_class(team_name=0)
    ia_1 = ai2_class(team_name=1)
    
    # Boucle de jeu
    turn = 0
    winner = None
    virtual_time = 0.0  # Temps simulé pour les cooldowns
    
    while turn < max_turns:
        turn += 1
        virtual_time += 0.1  # Chaque tour = 0.1s simulée (arbitraire mais suffisant pour reload)
        
        # Compter les survivants
        alive_0 = [s for s in game.all_soldats if s.team == 0 and s.is_alive]
        alive_1 = [s for s in game.all_soldats if s.team == 1 and s.is_alive]
        
        # Vérifier fin de partie
        if len(alive_0) == 0 and len(alive_1) == 0:
            winner = None
            break
        elif len(alive_0) == 0:
            winner = 1
            break
        elif len(alive_1) == 0:
            winner = 0
            break
        
        # Obtenir les actions des IAs
        actions_0 = ia_0.update(game)
        actions_1 = ia_1.update(game)
        all_actions = actions_0 + actions_1
        
        # Exécuter les actions
        for action in all_actions:
            if action[0] == "move":
                _, unit, dx, dy = action
                if unit.is_alive:
                    unit.move(game, dx=dx, dy=dy)
            elif action[0] == "attack":
                _, unit, target = action
                if unit.is_alive and target.is_alive:
                    unit.attack(target, current_time=virtual_time)
        
        # Nettoyer les morts
        game.all_soldats = [s for s in game.all_soldats if s.is_alive]
    
    return _get_result_dict(game, turn, winner, ai1_class, ai2_class, initial_counts)



def write_battle_report(result, ai1_name, ai2_name):
    """Écrit le rapport de bataille dans tournament_results.txt."""
    if result["winner"] == 0:
        winner_str = f"Équipe 0 ({ai1_name})"
        winning_ai = ai1_name
    elif result["winner"] == 1:
        winner_str = f"Équipe 1 ({ai2_name})"
        winning_ai = ai2_name
    else:
        winner_str = "Match Nul"
        winning_ai = "Aucune"
    
    report = f"""
========= FIN DE LA BATAILLE =========
VAINQUEUR : {winner_str}
IA GAGNANTE : {winning_ai}
Tours : {result['turns']}
Unités initiales 0 : {result['initial_counts'][0]}
Unités initiales 1 : {result['initial_counts'][1]}
Unités restantes 0 : {result['remaining_counts'][0]}
Unités restantes 1 : {result['remaining_counts'][1]}
PV Totaux 0 : {result['remaining_hp'][0]}
PV Totaux 1 : {result['remaining_hp'][1]}
======================================
"""
    with open("tournament_results.txt", "a", encoding="utf-8") as f:
        f.write(report + "\n")


# ============================================================
#                   CONFIGURATION CONSOLE
# ============================================================

def demander_compo(nom_equipe):
    """Demande à l'utilisateur la composition d'une équipe via la console."""
    print(f"\n--- CONFIGURATION {nom_equipe} ---")
    compo = {}
    
    try:
        h = input(f"Nombre de Hallebardiers (Halberdier) pour {nom_equipe} ? (defaut 20) : ")
        compo["Halberdier"] = int(h) if h.strip() else 20
        
        p = input(f"Nombre de Paladins (Paladin) pour {nom_equipe} ? (defaut 20) : ")
        compo["Paladin"] = int(p) if p.strip() else 20
        
        a = input(f"Nombre d'Arbalétriers (Arbalester) pour {nom_equipe} ? (defaut 20) : ")
        compo["Arbalester"] = int(a) if a.strip() else 20
        
    except ValueError:
        print("Entrée invalide détectée. Valeurs par défaut appliquées (20, 20, 20).")
        return {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
        
    return compo


# ============================================================
#                   MODE GRAPHIQUE (PYGAME)
# ============================================================

def run_graphical_battle(config_0, config_1, ai1_class, ai2_class, load_file=None):
    """Lance une bataille avec l'interface graphique Pygame."""
    import pygame
    import curses
    
    pygame.init()
    
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Bataille Médiévale")
    
    # Création du jeu
    game_map = Map("./assets/image.png", screen.get_rect())
    game = Game(game_map, SCREEN_WIDTH // 64, SCREEN_HEIGHT // 64)
    
    # Gestion du chargement
    is_loaded = False
    if load_file:
        is_loaded = load_game_state(game, load_file)
        if is_loaded:
            print(f"[*] Partie chargée depuis {load_file}")
    
    # Minimap
    minimap_original = pygame.image.load("./assets/image.png").convert()
    
    # Correction Minimap: Upscale 1.5x pour correspondre à la map physique
    w = minimap_original.get_width()
    h = minimap_original.get_height()
    minimap_original = pygame.transform.scale(minimap_original, (int(w * 1.5), int(h * 1.5)))
    
    MINIMAP_W, MINIMAP_H = 200, 113
    orig_ratio = minimap_original.get_width() / minimap_original.get_height()
    if orig_ratio > MINIMAP_W / MINIMAP_H:
        final_mm_w = MINIMAP_W
        final_mm_h = int(MINIMAP_W / orig_ratio)
    else:
        final_mm_h = MINIMAP_H
        final_mm_w = int(MINIMAP_H * orig_ratio)
    
    minimap_img = pygame.transform.smoothscale(minimap_original, (final_mm_w, final_mm_h))
    minimap_scale = final_mm_w / minimap_original.get_width()
    
    # IAs
    ia_0 = ai1_class(team_name=0)
    ia_1 = ai2_class(team_name=1)
    
    # Création des soldats
    if not is_loaded:
        full_config = {0: config_0, 1: config_1}
        game.create_soldat(full_config, ai_team0=ia_0, ai_team1=ia_1)
    
    # Thread console (curses)
    def run_curses(g):
        try:
            curses.wrapper(g.start_cmd)
        except:
            pass
    
    t = threading.Thread(target=run_curses, args=(game,))
    t.daemon = True
    t.start()
    
    # Boucle de jeu
    running = True
    clock = pygame.time.Clock()
    pygame.font.init()
    font = pygame.font.SysFont(None, 40)
    font_victory = pygame.font.SysFont(None, 150, bold=True)
    
    soldat_selectionne = None
    winner_text = ""
    paused = False
    notification_text = ""
    notification_time = 0
    NOTIFICATION_DURATION = 2.0
    image_cache = {}
    last_scale = -1
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_F11:
                    save_game_state(game, "quicksave.dat")
                    notification_text = "Sauvegarde effectuée"
                    notification_time = time.time()
                elif event.key == pygame.K_F12:
                    load_game_state(game, "quicksave.dat")
                    notification_text = "Chargement effectué"
                    notification_time = time.time()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                soldat_selectionne = None
                for unit in game.all_soldats:
                    sx, sy = game_map.nouvelle_map(unit.rect.x, unit.rect.y)
                    w, h = unit.rect.width * game_map.current_scale, unit.rect.height * game_map.current_scale
                    if pygame.Rect(sx, sy, w, h).collidepoint(event.pos):
                        soldat_selectionne = unit
                        break
            
            game_map.mouvement(event)
        
        # Logique
        if not winner_text and not paused:
            for soldat in list(game.all_soldats):
                if not soldat.is_alive:
                    game.remove_soldat(soldat)
            
            nb_alive_0 = len([u for u in game.all_soldats if u.team == 0])
            nb_alive_1 = len([u for u in game.all_soldats if u.team == 1])
            
            if nb_alive_0 == 0 and nb_alive_1 == 0:
                winner_text = "MATCH NUL !"
                check_end_and_report(game)
            elif nb_alive_0 == 0:
                winner_text = "VICTOIRE ROUGE !"
                check_end_and_report(game)
            elif nb_alive_1 == 0:
                winner_text = "VICTOIRE BLEUE !"
                check_end_and_report(game)
            else:
                actions_A = ia_1.update(game)
                actions_B = ia_0.update(game)
                all_actions = actions_A + actions_B
                
                for action in all_actions:
                    if action[0] == "move":
                        _, unit, dx, dy = action
                        unit.move(game, dx=dx, dy=dy)
                    elif action[0] == "attack":
                        _, unit, target = action
                        if getattr(target, "is_alive", False):
                            unit.attack(target)
        
        # Affichage
        screen.fill((0, 0, 0))
        game_map.draw(screen)
        
        current_scale = game_map.current_scale
        if current_scale != last_scale:
            image_cache.clear()
            last_scale = current_scale
        
        for unit in game.all_soldats:
            if hasattr(unit, 'update_animation'):
                unit.update_animation()
            
            world_x, world_y = unit.rect.x, unit.rect.y
            screen_x, screen_y = game_map.nouvelle_map(world_x, world_y)
            soldat_w = int(unit.rect.width * current_scale)
            soldat_h = int(unit.rect.height * current_scale)
            
            if soldat_w > 0 and soldat_h > 0:
                cache_key = (id(unit.image), soldat_w, soldat_h)
                if cache_key not in image_cache:
                    image_cache[cache_key] = pygame.transform.scale(unit.image, (soldat_w, soldat_h))
                
                screen.blit(image_cache[cache_key], (screen_x, screen_y))
                
                # Barre de vie
                hp_ratio = unit.hp / unit.max_hp
                bar_width = int(soldat_w * 0.7)
                bar_height = max(2, int(3 * current_scale))
                bar_x = screen_x + (soldat_w - bar_width) // 2
                bar_y = screen_y - bar_height - 1
                
                pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                if unit.team == 0:
                    # Equipe 0 (Bleu) : Cyan -> Bleu foncé
                    bar_color = (0, int(255 * hp_ratio), 255)
                else:
                    # Equipe 1 (Rouge) : Orange -> Rouge foncé
                    bar_color = (255, int(100 * hp_ratio), 0)
                hp_width = int(bar_width * hp_ratio)
                if hp_width > 0:
                    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, hp_width, bar_height))
                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Minimap
        actual_screen_w = screen.get_width()
        actual_screen_h = screen.get_height()
        mm_margin = 15
        mm_x = actual_screen_w - final_mm_w - mm_margin
        mm_y = mm_margin
        
        pygame.draw.rect(screen, (30, 30, 30), (mm_x - 5, mm_y - 5, final_mm_w + 10, final_mm_h + 10))
        pygame.draw.rect(screen, (180, 140, 60), (mm_x - 5, mm_y - 5, final_mm_w + 10, final_mm_h + 10), 4)
        screen.blit(minimap_img, (mm_x, mm_y))
        
        view_x = -game_map.rect.x / game_map.current_scale * minimap_scale
        view_y = -game_map.rect.y / game_map.current_scale * minimap_scale
        view_w = actual_screen_w / game_map.current_scale * minimap_scale
        view_h = actual_screen_h / game_map.current_scale * minimap_scale
        viewport = pygame.Rect(mm_x + view_x, mm_y + view_y, view_w, view_h)
        viewport = viewport.clip(pygame.Rect(mm_x, mm_y, final_mm_w, final_mm_h))
        if viewport.width > 0 and viewport.height > 0:
            pygame.draw.rect(screen, (255, 50, 50), viewport, 2)
        
        for unit in game.all_soldats:
            soldier_mm_x = mm_x + int(unit.rect.centerx * minimap_scale)
            soldier_mm_y = mm_y + int(unit.rect.centery * minimap_scale)
            dot_color = (50, 100, 255) if unit.team == 0 else (255, 50, 50)
            pygame.draw.circle(screen, dot_color, (soldier_mm_x, soldier_mm_y), 2)
        
        if soldat_selectionne and soldat_selectionne.is_alive:
            texte = f"{soldat_selectionne.name} : {soldat_selectionne.hp} PV"
            screen.blit(font.render(texte, True, (255, 255, 255)), (20, SCREEN_HEIGHT - 50))
        
        if winner_text:
            color_gold = (255, 215, 0)
            text_surf = font_victory.render(winner_text, True, color_gold)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            outline_surf = font_victory.render(winner_text, True, (0, 0, 0))
            outline_rect = outline_surf.get_rect(center=(SCREEN_WIDTH // 2 + 5, SCREEN_HEIGHT // 2 + 5))
            screen.blit(outline_surf, outline_rect)
            screen.blit(text_surf, text_rect)
        
        if paused and not winner_text:
            nb_bleus = len([u for u in game.all_soldats if u.team == 0])
            nb_rouges = len([u for u in game.all_soldats if u.team == 1])
            
            pause_overlay = pygame.Surface((600, 300), pygame.SRCALPHA)
            pause_overlay.fill((0, 0, 0, 180))
            screen.blit(pause_overlay, (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 150))
            
            pygame.draw.rect(screen, (212, 175, 55), (SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 150, 600, 300), 4)
            
            color_gold = (212, 175, 55)
            pause_title = font_victory.render("~ Pause ~", True, color_gold)
            title_rect = pause_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            screen.blit(pause_title, title_rect)
            
            font_pause = pygame.font.SysFont(None, 50)
            bleu_text = font_pause.render(f"Armée Bleue: {nb_bleus} soldats", True, (100, 150, 255))
            bleu_rect = bleu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
            screen.blit(bleu_text, bleu_rect)
            
            rouge_text = font_pause.render(f"Armée Rouge: {nb_rouges} soldats", True, (255, 100, 100))
            rouge_rect = rouge_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(rouge_text, rouge_rect)
            
            font_small = pygame.font.SysFont(None, 30)
            hint_text = font_small.render("Appuyez sur ESPACE pour reprendre", True, (180, 180, 180))
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
            screen.blit(hint_text, hint_rect)
        
        # Notifications
        if notification_text and (time.time() - notification_time) < NOTIFICATION_DURATION:
            time_remaining = NOTIFICATION_DURATION - (time.time() - notification_time)
            alpha = min(255, int(255 * (time_remaining / 1.0))) if time_remaining < 1.0 else 255
            
            font_notif = pygame.font.SysFont(None, 35)
            notif_surf = font_notif.render(notification_text, True, (255, 255, 255))
            notif_w = notif_surf.get_width() + 30
            notif_h = notif_surf.get_height() + 20
            notif_x = actual_screen_w - notif_w - 20
            notif_y = actual_screen_h - notif_h - 20
            
            notif_bg = pygame.Surface((notif_w, notif_h), pygame.SRCALPHA)
            notif_bg.fill((40, 40, 40, min(200, alpha)))
            screen.blit(notif_bg, (notif_x, notif_y))
            
            pygame.draw.rect(screen, (212, 175, 55), (notif_x, notif_y, notif_w, notif_h), 2)
            
            notif_text_alpha = notif_surf.copy()
            notif_text_alpha.set_alpha(alpha)
            screen.blit(notif_text_alpha, (notif_x + 15, notif_y + 10))
        elif notification_text:
            notification_text = ""
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


# ============================================================
#                   COMMANDES CLI
# ============================================================

def _run_batch_battle(args):
    """Helper pour le multiprocessing: unpack args et lance run_headless_battle"""
def _run_batch_battle(args):
    """Helper pour le multiprocessing: unpack args et lance run_headless_battle"""
    config_0, config_1, ai1_class, ai2_class = args
    # OPTIMISATION PLOT: Map réduite (30x20) pour forcer le combat rapide + max_turns réduit
    return run_headless_battle(config_0, config_1, ai1_class, ai2_class, max_turns=2000, width=30, height=20)

def cmd_plot(args):
    """Génère un graphique (loi de Lanchester) - Optimisé Multiprocess."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("[!] Matplotlib introuvable. Installez-le avec: pip install matplotlib")
        return
        
    import concurrent.futures
    import os

    ai1_class = get_ai_class(args.ai1)
    ai2_class = get_ai_class(args.ai2)
    
    unit_type = args.unit
    
    # Parsing range string `range(1,100)` or `1-100`
    import re
    range_str = args.range
    min_val, max_val = 1, 50
    
    match = re.search(r'range\(\s*(\d+)\s*,\s*(\d+)\s*\)', range_str)
    if match:
        min_val = int(match.group(1))
        max_val = int(match.group(2))
    elif '-' in range_str:
        try:
            parts = range_str.split('-')
            min_val = int(parts[0])
            max_val = int(parts[1])
        except:
             print(f"[!] Format de plage invalide: {range_str}. Utilisez range(1,100) ou 1-100")
             return
    else:
         print(f"[!] Format de plage inconnu: {range_str}")
         return
    
    print(f"[*] Plotting: {args.ai1} vs {args.ai2}")
    print(f"[*] Variation: {unit_type} de {min_val} à {max_val} (Rounds: {args.rounds})")
    print(f"[*] Parallélisme: {os.cpu_count()} coeurs")
    
    x_values = []
    y_win_rates = []
    
    # Config fixe de l'adversaire
    config_1_fixed = {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
    
    # Préparation de toutes les tâches
    tasks = []
    total_sims = (max_val - min_val + 1) * args.rounds
    
    # Pour chaque quantité d'unité
    for count in range(min_val, max_val + 1):
        config_0 = {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
        config_0[unit_type] = count
        
        # On prépare N batailles pour ce count
        for _ in range(args.rounds):
            tasks.append((config_0.copy(), config_1_fixed.copy(), ai1_class, ai2_class))

    print(f"[*] Lancement de {total_sims} simulations...")
    
    results = []
    completed = 0
    
    # Exécution parallèle
    path_py = os.sys.executable
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # submit all
        future_to_task = {executor.submit(_run_batch_battle, task): task for task in tasks}
        
        for future in concurrent.futures.as_completed(future_to_task):
            completed += 1
            if completed % 10 == 0 or completed == total_sims:
                print(f"\rProgression: {completed}/{total_sims} simulations", end="", flush=True)
            
            try:
                res = future.result()
                results.append(res)
            except Exception as e:
                print(f"\n[!] Erreur simu: {e}")

    print("\n[*] Analyse des résultats...")
    
    # Agrégation des résultats
    # Il faut mapper les résultats au 'count' qui a généré la config
    # On sait que l'ordre n'est pas garanti, mais on peut reconstruire
    # On va refaire une boucle simple pour le plotting en filtrant les résultats
    # Une méthode plus robuste aurait été de passer le 'count' dans le retour
    
    # Re-tri par count
    stats_by_count = {c: {"wins": 0, "total": 0} for c in range(min_val, max_val + 1)}
    
    # On a besoin de savoir quel résultat correspond à quel count.
    # Hack simple: on regarde le count de unit_type dans initial_counts du résultat
    
    for res in results:
        # res['initial_counts'] = {0: ..., 1: ...} -> NON, c'est la somme total
        # Ah, run_headless_battle ne retourne pas le détail par unité dans le dict result standard
        # Il faut modifier run_headless_battle ou _run_batch_battle pour retourner le count
        pass
        
    # CORRECTION : On va modifier _run_batch_battle pour qu'il retourne aussi le count testé
    # Mais wait, je ne peux pas redéfinir _run_batch_battle facilement sans changer tout le bloc
    
    # On va le faire différemment: On exécute par lots de 'count'
    pass 
    
    # --- Approche itérative par count avec parallélisme sur les rounds ---
    x_values = range(min_val, max_val + 1)
    y_win_rates = []
    
    current_idx = 0
    total_steps = len(x_values)
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for count in x_values:
            current_idx += 1
            print(f"\rAnalysing {unit_type}={count} ({current_idx}/{total_steps})...", end="", flush=True)
            
            config_0 = {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
            config_0[unit_type] = count
            
            # Lancer les N rounds en parallèle pour CE count
            batch_tasks = [(config_0.copy(), config_1_fixed.copy(), ai1_class, ai2_class) for _ in range(args.rounds)]
            
            futures = [executor.submit(_run_batch_battle, t) for t in batch_tasks]
            
            wins = 0
            for f in concurrent.futures.as_completed(futures):
                if f.result()["winner"] == 0:
                    wins += 1
            
            y_win_rates.append((wins / args.rounds) * 100)

    print("\n[*] Génération du graphique...")
    
    plt.figure(figsize=(10, 6))
    plt.plot(list(x_values), y_win_rates, marker='o', linestyle='-', color='b')
    plt.title(f"Win Rate of {args.ai1} vs {args.ai2}")
    plt.xlabel(f"Number of {unit_type}")
    plt.ylabel("Win Rate (%)")
    plt.grid(True)
    plt.axhline(y=50, color='r', linestyle='--', label="50% Win Rate")
    plt.legend()
    
    filename = f"plot_{args.ai1}_vs_{args.ai2}_{unit_type}.png"
    plt.savefig(filename)
    print(f"[*] Graphique sauvegardé: {filename}")
    plt.show()

def cmd_run(args):
    """Exécute une bataille."""
    ai1_class = get_ai_class(args.ai1)
    ai2_class = get_ai_class(args.ai2)
    
    print(f"[*] Bataille: {args.ai1} vs {args.ai2}")
    
    
    # Récupérer la config du scénario
    # FORCE STANDARD CHECK pour rassurer l'utilisateur
    if args.scenario.lower() == "standard":
        config_0 = {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
        config_1 = {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
        print("[DEBUG] SCENARIO STANDARD FORCE (20/20/20)")
    else:
        config_0, config_1 = get_scenario_configs(args.scenario)
    
        
    print(f"[*] Bataille: {args.ai1} vs {args.ai2}")
    print(f"[*] Config Equipe 0: {config_0}")
    print(f"[*] Config Equipe 1: {config_1}")
    
    if args.terminal:
        # Mode terminal (curses)
        print("[*] Mode terminal (curses)")
        import curses
        try:
             # Utiliser curses.wrapper pour gérer l'init/cleanup
            result = curses.wrapper(run_curses_battle, config_0, config_1, ai1_class, ai2_class)
        except curses.error as e:
            print(f"Erreur Curses: {e}")
            print("Note: Curses peut ne pas fonctionner correctement sous certains terminaux Windows sans 'windows-curses'.")
            return

        if result:
            winner_str = "Match Nul" if result["winner"] is None else f"Équipe {result['winner']}"
            print(f"\n[*] Résultat: {winner_str} en {result['turns']} tours")
            
            write_battle_report(result, args.ai1, args.ai2)
            print("[*] Rapport écrit dans tournament_results.txt")
            
            if args.datafile:
                with open(args.datafile, "a", encoding="utf-8") as f:
                    f.write(f"{result}\n")
    else:
        # Mode graphique
        run_graphical_battle(config_0, config_1, ai1_class, ai2_class)


def cmd_load(args):
    """Charge une sauvegarde."""
    print(f"[*] Chargement de {args.savefile}")
    
    config_0 = {"Halberdier": 0, "Paladin": 0, "Arbalester": 0}
    config_1 = {"Halberdier": 0, "Paladin": 0, "Arbalester": 0}
    
    run_graphical_battle(config_0, config_1, ColonelSMART, MajorDaftSimple, load_file=args.savefile)


def cmd_tourney(args):
    """Lance un tournoi automatique."""
    ai_classes = [get_ai_class(name) for name in args.ais]
    
    print(f"[*] Tournoi: {len(ai_classes)} IAs, {args.rounds} rounds")
    print(f"    IAs: {args.ais}")
    print(f"    Alternance positions: {not args.no_alternate}")
    
    results = {}
    results = {}
    config_0, config_1 = get_scenario_configs(args.scenario)
    
    # Toutes les combinaisons
    from itertools import combinations
    matchups = list(combinations(ai_classes, 2))
    
    total_battles = len(matchups) * args.rounds
    if not args.no_alternate:
        total_battles *= 2
    
    print(f"[*] {total_battles} batailles à exécuter...")
    
    battle_count = 0
    for ai1, ai2 in matchups:
        key = f"{ai1.__name__} vs {ai2.__name__}"
        results[key] = {"wins": 0, "losses": 0, "draws": 0}
        
        for r in range(args.rounds):
            battle_count += 1
            print(f"\r[{battle_count}/{total_battles}] {key} (round {r+1})", end="", flush=True)
            
            result = run_headless_battle(config_0, config_1, ai1, ai2)
            write_battle_report(result, ai1.__name__, ai2.__name__)
            
            if result["winner"] == 0:
                results[key]["wins"] += 1
            elif result["winner"] == 1:
                results[key]["losses"] += 1
            else:
                results[key]["draws"] += 1
        
        # Position inversée
        if not args.no_alternate:
            key_inv = f"{ai2.__name__} vs {ai1.__name__}"
            results[key_inv] = {"wins": 0, "losses": 0, "draws": 0}
            
            for r in range(args.rounds):
                battle_count += 1
                print(f"\r[{battle_count}/{total_battles}] {key_inv} (round {r+1})", end="", flush=True)
                
                result = run_headless_battle(config_0, config_1, ai2, ai1)
                write_battle_report(result, ai2.__name__, ai1.__name__)
                
                if result["winner"] == 0:
                    results[key_inv]["wins"] += 1
                elif result["winner"] == 1:
                    results[key_inv]["losses"] += 1
                else:
                    results[key_inv]["draws"] += 1
    
    print("\n\n" + "=" * 50)
    print("RÉSULTATS DU TOURNOI")
    print("=" * 50)
    for matchup, stats in results.items():
        total = stats["wins"] + stats["losses"] + stats["draws"]
        win_rate = (stats["wins"] / total * 100) if total > 0 else 0
        print(f"{matchup}: {stats['wins']}W / {stats['losses']}L / {stats['draws']}D ({win_rate:.1f}%)")
    print("=" * 50)
    print("[*] Tous les résultats sont dans tournament_results.txt")


# ============================================================
#                   POINT D'ENTRÉE PRINCIPAL
# ============================================================

def main():
    epilog_text = """
EXEMPLES D'UTILISATION :
------------------------
Possible IA : ColonelSMART  -  MajorDaftSimple  -  
1. BATAILLE SIMPLE (Mode Graphique)
   python battle.py run ColonelSMART MajorDaftSimple

2. BATAILLE SIMPLE (Mode Terminal Rapide)
   python battle.py run ColonelSMART MajorDaftSimple -t

3. SCÉNARIOS PRÉDÉFINIS
   python battle.py run ColonelSMART MajorDaftSimple -t -S Horde
   Scénarios dispos : Standard, Small, Duel, Archers, Horde

4. TOURNOI AUTOMATIQUE
   python battle.py tourney -G ColonelSMART MajorDaftSimple -N 10 -S Duel

5. GRAPHIQUE D'ANALYSE (Loi de Lanchester)
   python battle.py plot ColonelSMART MajorDaft -N 5 --unit Halberdier --range "range(1,50)"

6. CHARGER UNE SAUVEGARDE
   python battle.py load quicksave.dat

COMMANDES DISPONIBLES :
-----------------------
  run       Lancer une bataille unique
  tourney   Lancer un tournoi (plusieurs rounds)
  plot      Générer un graphique de performance
  load      Charger une sauvegarde existante
"""
    parser = argparse.ArgumentParser(
        prog="battle.py",
        description="Simulation de Bataille Médiévale - Outil Unifié",
        epilog=epilog_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # === Commande RUN ===
    run_parser = subparsers.add_parser("run", help="Lancer une bataille")
    run_parser.add_argument("ai1", help="IA équipe 0 (ex: ColonelSMART, MajorDaft)")
    run_parser.add_argument("ai2", help="IA équipe 1")
    run_parser.add_argument("-t", "--terminal", action="store_true",
                           help="Mode terminal (headless) au lieu de graphique")
    run_parser.add_argument("-S", "--scenario", type=str, default="Standard",
                           help="Scénario (Standard, Small, Duel, Archers, Horde)")
    run_parser.add_argument("-d", "--datafile", type=str, default=None,
                           help="Fichier où écrire les données")
    
    # === Commande LOAD ===
    load_parser = subparsers.add_parser("load", help="Charger une sauvegarde")
    load_parser.add_argument("savefile", help="Fichier de sauvegarde")
    
    # === Commande TOURNEY ===
    tourney_parser = subparsers.add_parser("tourney", help="Lancer un tournoi")
    tourney_parser.add_argument("-G", "--ais", nargs="+",
                               default=["ColonelSMART", "MajorDaftSimple"],
                               help="Liste des IAs")
    tourney_parser.add_argument("-N", "--rounds", type=int, default=10,
                               help="Nombre de rounds par matchup")
    tourney_parser.add_argument("-S", "--scenario", type=str, default="Standard",
                               help="Scénario (Standard, Small, Duel, Archers, Horde)")
    tourney_parser.add_argument("-na", "--no-alternate", action="store_true",
                               help="Ne pas alterner les positions")
    
    # === Commande PLOT ===
    plot_parser = subparsers.add_parser("plot", help="Générer un graphique de performance")
    plot_parser.add_argument("ai1", help="IA équipe variable (ex: ColonelSMART)")
    plot_parser.add_argument("ai2", help="IA équipe fixe (adversaire)")
    plot_parser.add_argument("--unit", type=str, default="Halberdier",
                            help="Type d'unité à varier")
    plot_parser.add_argument("--range", type=str, default="range(1,50)",
                            help="Plage: 'range(min,max)' ou 'min-max'")
    plot_parser.add_argument("-N", "--rounds", type=int, default=5,
                            help="Rounds par point")
    
    args = parser.parse_args()
    
    # Si aucune commande, mode interactif graphique par défaut
    if args.command is None:
        print("=== BATAILLE MÉDIÉVALE : CONFIGURATION ===")
        config_0 = demander_compo("EQUIPE BLEUE (0)")
        config_1 = demander_compo("EQUIPE ROUGE (1)")
        
        print("\nLancement de la simulation...")
        time.sleep(1)
        
        run_graphical_battle(config_0, config_1, ColonelSMART, MajorDaftSimple)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "load":
        cmd_load(args)
    elif args.command == "tourney":
        cmd_tourney(args)
    elif args.command == "plot":
        cmd_plot(args)


if __name__ == "__main__":
    main()
