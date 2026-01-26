import argparse
import sys
import os
import time
import threading
import math

from src.map import Map
from src.game import Game
from src.ai_daft import MajorDaftSimple
from src.ia_braindead import GeneralBrainDead
from src.ColonelSMART import ColonelSMART
from src.save_manager import save_game_state, load_game_state
from src.stats_generator import check_end_and_report
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRE DES IA : Dictionnaire des IA disponibles avec leurs alias
# Permet d'accéder aux classes IA par leur nom en ligne de commande
# ═══════════════════════════════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════════════════════════════
# SCÉNARIOS : Configurations prédéfinies pour différents types de batailles
# Standard (60v60), Small, Duel, Archers only, et Horde
# ═══════════════════════════════════════════════════════════════════════════════
def get_scenario_configs(name):
    name = name.lower()
    
    if name == "standard":
        c = {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
        return c.copy(), c.copy()
        
    elif name == "small":
        c = {"Halberdier": 5, "Paladin": 2, "Arbalester": 2}
        return c.copy(), c.copy()
        
    elif name == "duel":
        return {"Paladin": 1}, {"Halberdier": 1}
        
    elif name == "archers":
        c = {"Arbalester": 30}
        return c.copy(), c.copy()
        
    elif name == "horde":
        return {"Halberdier": 50}, {"Paladin": 10, "Arbalester": 10}
        
    else:
        print(f"[!] Scénario '{name}' inconnu. Utilisation de 'Standard'.")
        c = {"Halberdier": 20, "Paladin": 20, "Arbalester": 20}
        return c.copy(), c.copy()

def get_ai_class(name):
    if name in AI_REGISTRY:
        return AI_REGISTRY[name]
    raise ValueError(f"IA inconnue: {name}. Disponibles: {list(AI_REGISTRY.keys())}")


# ═══════════════════════════════════════════════════════════════════════════════
# MODE HEADLESS : Version du jeu sans affichage graphique pour les tournois
# Classe simplifiée qui gère uniquement la logique de combat
# ═══════════════════════════════════════════════════════════════════════════════
class HeadlessGame:
    
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


# ═══════════════════════════════════════════════════════════════════════════════
# SETUP HEADLESS : Prépare une partie headless avec les soldats des deux équipes
# Place les unités en colonnes sur les côtés gauche et droit de la carte
# ═══════════════════════════════════════════════════════════════════════════════
def _setup_headless_game(config_0, config_1, width=60, height=34):
    game = HeadlessGame(width=width, height=height)
    
    class_map = {
        "Halberdier": Halberdier,
        "Paladin": Paladin,
        "Arbalester": Arbalester
    }
    
    def normalize_key(key):
        key_lower = key.lower()
        if "halber" in key_lower or "halbar" in key_lower:
            return "Halberdier"
        elif "paladin" in key_lower:
            return "Paladin"
        elif "arbal" in key_lower:
            return "Arbalester"
        return key
    
    start_x, start_y = 2, 5
    col = 0
    for unit_type, count in config_0.items():
        normalized = normalize_key(unit_type)
        if normalized not in class_map:
            print(f"[!] Type d'unité inconnu ignoré: {unit_type}")
            continue
        for i in range(count):
            soldat = class_map[normalized](start_x + col, start_y + i, 0)
            game.add_soldat(soldat)
        col += 1
    
    start_x = game.width - 3
    col = 0
    for unit_type, count in config_1.items():
        normalized = normalize_key(unit_type)
        if normalized not in class_map:
            print(f"[!] Type d'unité inconnu ignoré: {unit_type}")
            continue
        for i in range(count):
            soldat = class_map[normalized](start_x - col, start_y + i, 1)
            game.add_soldat(soldat)
        col += 1
        
    return game



# ═══════════════════════════════════════════════════════════════════════════════
# BATAILLE CURSES : Mode terminal avec affichage ASCII en temps réel
# Utilise la bibliothèque curses pour l'affichage console coloré
# ═══════════════════════════════════════════════════════════════════════════════
def run_curses_battle(stdscr, config_0, config_1, ai1_class, ai2_class):
    import curses
    import pygame
    
    if not pygame.display.get_init():
        pygame.display.init()
    if not pygame.display.get_surface():
        pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1)
    
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    game = _setup_headless_game(config_0, config_1)
    
    ia_0 = ai1_class(team_name=0)
    ia_1 = ai2_class(team_name=1)
    
    turn = 0
    paused = False
    KEY_REPEAT = 5 
    
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            return None
        elif key == ord('p') or key == ord(' '):
            paused = not paused
        
        turns_to_process = KEY_REPEAT if not paused else 0
        
        alive_0 = [s for s in game.all_soldats if s.team == 0 and s.is_alive]
        alive_1 = [s for s in game.all_soldats if s.team == 1 and s.is_alive]
        
        winner = None
        if not alive_0 and not alive_1: winner = -1 
        elif not alive_0: winner = 1
        elif not alive_1: winner = 0
            
        if winner is not None:
            stdscr.addstr(game.height + 2, 0, f"FIN DE LA PARTIE ! Vainqueur: {'EQUIPE 1' if winner==1 else 'EQUIPE 0' if winner==0 else 'EGALITE'}", curses.A_BOLD)
            stdscr.addstr(game.height + 3, 0, "Appuyez sur 'q' pour quitter.", curses.A_BLINK)
            stdscr.refresh()
            stdscr.timeout(-1)
            while True:
                kp = stdscr.getch()
                if kp == ord('q'): return _get_result_dict(game, turn, winner, ai1_class, ai2_class, _get_initial_counts(config_0, config_1))

        for _ in range(turns_to_process):
            turn += 1
            actions_0 = ia_0.update(game)
            actions_1 = ia_1.update(game)
            all_actions = actions_0 + actions_1
            
            for action in all_actions:
                if action[0] == "move":
                    _, unit, dx, dy = action
                    if unit.is_alive:
                        unit.move(game, dx=dx, dy=dy)
                elif action[0] == "attack":
                    _, unit, target = action
                    if unit.is_alive and target.is_alive:
                        unit.attack(target)
            
            game.all_soldats = [s for s in game.all_soldats if s.is_alive]
            
            alive_0 = [s for s in game.all_soldats if s.team == 0 and s.is_alive]
            alive_1 = [s for s in game.all_soldats if s.team == 1 and s.is_alive]
            if not alive_0 or not alive_1:
                break
        
        try:
            stdscr.erase()
            max_y, max_x = stdscr.getmaxyx()
            
            header1 = f"Tour: {turn} | {'PAUSE' if paused else 'EN COURS'} | (q: quitter, p: pause)"
            header2 = f"Bleus: {len(alive_0)} | Rouges: {len(alive_1)}"
            
            if max_y < game.height + 5 or max_x < game.width + 2:
                stdscr.addstr(0, 0, "Terminal trop petit !", curses.color_pair(3))
                stdscr.addstr(1, 0, f"Requis: {game.width+2}x{game.height+5}", curses.color_pair(3))
                stdscr.addstr(2, 0, f"Actuel: {max_x}x{max_y}", curses.color_pair(3))
                stdscr.refresh()
                continue
                
            stdscr.addstr(0, 0, header1[:max_x-1], curses.color_pair(3))
            stdscr.addstr(1, 0, header2[:max_x-1], curses.color_pair(3))
            
            offset_y = 3
            stdscr.addstr(offset_y - 1, 0, "+" + "-"*game.width + "+")
            stdscr.addstr(offset_y + game.height, 0, "+" + "-"*game.width + "+")
            
            for y in range(game.height):
                stdscr.addch(offset_y + y, 0, "|")
                try:
                    stdscr.addch(offset_y + y, game.width + 1, "|")
                except: pass
                
            display_grid = {}
            for s in game.all_soldats:
                gx, gy = int(s.rect.x // 32), int(s.rect.y // 32)
                if 0 <= gx < game.width and 0 <= gy < game.height:
                    display_grid[(gx, gy)] = s
            
            for y in range(game.height):
                for x in range(game.width):
                    scr_y = offset_y + y
                    scr_x = x + 1
                    
                    if 0 <= scr_y < max_y and 0 <= scr_x < max_x:
                        if (x, y) in display_grid:
                            s = display_grid[(x, y)]
                            char = s.tag
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
            pass

def _get_initial_counts(c0, c1):
    return {0: sum(c0.values()), 1: sum(c1.values())}

def _get_result_dict(game, turn, winner, ai1, ai2, initial_counts):
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


# ═══════════════════════════════════════════════════════════════════════════════
# BATAILLE HEADLESS : Mode 100% sans affichage pour les tournois rapides
# Simule la bataille tour par tour avec un temps virtuel pour les cooldowns
# track_history=True pour enregistrer l'évolution des unités à chaque tour
# ═══════════════════════════════════════════════════════════════════════════════
def run_headless_battle(config_0, config_1, ai1_class, ai2_class, max_turns=10000, width=60, height=34, track_history=False):
    import pygame
    
    if not pygame.display.get_init():
        pygame.display.init()
    if not pygame.display.get_surface():
            pygame.display.set_mode((1, 1), pygame.HIDDEN)
            
    game = _setup_headless_game(config_0, config_1, width=width, height=height)
    initial_counts = _get_initial_counts(config_0, config_1)

    ia_0 = ai1_class(team_name=0)
    ia_1 = ai2_class(team_name=1)
    
    turn = 0
    winner = None
    virtual_time = 0.0
    
    history_0 = []
    history_1 = []
    history_turns = []
    
    while turn < max_turns:
        turn += 1
        virtual_time += 0.1
        
        alive_0 = [s for s in game.all_soldats if s.team == 0 and s.is_alive]
        alive_1 = [s for s in game.all_soldats if s.team == 1 and s.is_alive]
        
        if track_history:
            history_turns.append(turn)
            history_0.append(len(alive_0))
            history_1.append(len(alive_1))
        
        if len(alive_0) == 0 and len(alive_1) == 0:
            winner = None
            break
        elif len(alive_0) == 0:
            winner = 1
            break
        elif len(alive_1) == 0:
            winner = 0
            break
        
        actions_0 = ia_0.update(game)
        actions_1 = ia_1.update(game)
        all_actions = actions_0 + actions_1
        
        for action in all_actions:
            if action[0] == "move":
                _, unit, dx, dy = action
                if unit.is_alive:
                    unit.move(game, dx=dx, dy=dy)
            elif action[0] == "attack":
                _, unit, target = action
                if unit.is_alive and target.is_alive:
                    unit.attack(target, current_time=virtual_time)
        
        game.all_soldats = [s for s in game.all_soldats if s.is_alive]
    
    result = _get_result_dict(game, turn, winner, ai1_class, ai2_class, initial_counts)
    
    if track_history:
        result["history"] = {
            "turns": history_turns,
            "team_0": history_0,
            "team_1": history_1
        }
    
    return result



# ═══════════════════════════════════════════════════════════════════════════════
# RAPPORT DE BATAILLE : Écrit les résultats dans statistiques/tournament_results.txt
# Inclut le vainqueur, les tours, les unités restantes et les PV totaux
# ═══════════════════════════════════════════════════════════════════════════════
def write_battle_report(result, ai1_name, ai2_name):
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
    if not os.path.exists("statistiques"):
        os.makedirs("statistiques")
    
    with open("statistiques/tournament_results.txt", "a", encoding="utf-8") as f:
        f.write(report + "\n")



# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION CONSOLE : Demande interactive de la composition des équipes
# Permet de personnaliser le nombre d'unités de chaque type
# ═══════════════════════════════════════════════════════════════════════════════
def demander_compo(nom_equipe):
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


# ═══════════════════════════════════════════════════════════════════════════════
# BATAILLE GRAPHIQUE : Mode visuel complet avec Pygame
# Affiche la carte, les unités animées, la minimap et les barres de vie
# ═══════════════════════════════════════════════════════════════════════════════
def run_graphical_battle(config_0, config_1, ai1_class, ai2_class, load_file=None):
    import pygame
    import curses
    
    pygame.init()
    
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Bataille Médiévale")
    
    game_map = Map("./assets/image.png", screen.get_rect())
    game = Game(game_map, SCREEN_WIDTH // 64, SCREEN_HEIGHT // 64)
    
    is_loaded = False
    if load_file:
        is_loaded = load_game_state(game, load_file)
        if is_loaded:
            print(f"[*] Partie chargée depuis {load_file}")
    
    minimap_original = pygame.image.load("./assets/image.png").convert()
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
    
    ia_0 = ai1_class(team_name=0)
    ia_1 = ai2_class(team_name=1)
    
    if not is_loaded:
        full_config = {0: config_0, 1: config_1}
        game.create_soldat(full_config, ai_team0=ia_0, ai_team1=ia_1)
    
    def run_curses(g):
        try:
            curses.wrapper(g.start_cmd)
        except:
            pass
    
    t = threading.Thread(target=run_curses, args=(game,))
    t.daemon = True
    t.start()
    
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
    

    # ═══════════════════════════════════════════════════════════════════════════════
    # BOUCLE PRINCIPALE : Gère les événements, la logique et l'affichage
    # ═══════════════════════════════════════════════════════════════════════════════
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
        

        # ═══════════════════════════════════════════════════════════════════════════════
        # RENDU GRAPHIQUE : Dessine la carte, les unités et l'interface utilisateur
        # ═══════════════════════════════════════════════════════════════════════════════
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
                
                hp_ratio = unit.hp / unit.max_hp
                bar_width = int(soldat_w * 0.7)
                bar_height = max(2, int(3 * current_scale))
                bar_x = screen_x + (soldat_w - bar_width) // 2
                bar_y = screen_y - bar_height - 1
                
                pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                if unit.team == 0:
                    bar_color = (0, int(255 * hp_ratio), 255)
                else:
                    bar_color = (255, int(100 * hp_ratio), 0)
                hp_width = int(bar_width * hp_ratio)
                if hp_width > 0:
                    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, hp_width, bar_height))
                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        

        # ═══════════════════════════════════════════════════════════════════════════════
        # MINIMAP : Affiche la carte réduite avec les positions des unités
        # ═══════════════════════════════════════════════════════════════════════════════
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
        

        # ═══════════════════════════════════════════════════════════════════════════════
        # ÉCRANS SPÉCIAUX : Affichage de la victoire et du menu pause
        # ═══════════════════════════════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER MULTIPROCESSING : Fonction wrapper pour les batailles en parallèle
# ═══════════════════════════════════════════════════════════════════════════════
def _run_batch_battle(args):
    config_0, config_1, ai1_class, ai2_class = args
    return run_headless_battle(config_0, config_1, ai1_class, ai2_class, max_turns=10000, width=50, height=40)


# ═══════════════════════════════════════════════════════════════════════════════
# COMMANDE LANCHESTER : Simule la loi de Lanchester (N fixe vs M croissant)
# Teste une armée fixe contre une armée ennemie de taille croissante
# ═══════════════════════════════════════════════════════════════════════════════
def cmd_plot(args):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("[!] Matplotlib/NumPy introuvable. Installez avec: pip install matplotlib numpy")
        return
        
    import concurrent.futures
    import os
    import re

    ai1_class = get_ai_class(args.ai1)
    ai2_class = get_ai_class(args.ai2)
    
    # Parse range
    range_str = args.range
    min_enemy, max_enemy = 1, 30
    
    match = re.search(r'range\(\s*(\d+)\s*,\s*(\d+)\s*\)', range_str)
    if match:
        min_enemy = int(match.group(1))
        max_enemy = int(match.group(2))
    elif '-' in range_str:
        try:
            parts = range_str.split('-')
            min_enemy = int(parts[0])
            max_enemy = int(parts[1])
        except:
            print(f"[!] Format de plage invalide: {range_str}")
            return
    
    # Fixed army size for team 0
    fixed_army = args.fixed
    unit_type = args.unit
    
    print("=" * 60)
    print("        LOI DE LANCHESTER - SIMULATION")
    print("=" * 60)
    print(f"[*] Armée fixe (Équipe 0): {fixed_army} {unit_type}")
    print(f"[*] Armée ennemie (Équipe 1): {min_enemy} à {max_enemy} {unit_type}")
    print(f"[*] IA: {args.ai1} vs {args.ai2}")
    print(f"[*] Rounds par point: {args.rounds}")
    print(f"[*] Parallélisme: {os.cpu_count()} coeurs")
    print("=" * 60)
    
    x_enemy_counts = list(range(min_enemy, max_enemy + 1))
    y_survivors_A = []  
    y_survivors_B = []  
    
    total_steps = len(x_enemy_counts)
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for idx, enemy_count in enumerate(x_enemy_counts):
            print(f"\r[{idx+1}/{total_steps}] Test: {fixed_army} vs {enemy_count}...", end="", flush=True)
            
            # Config: équipe 0 fixe, équipe 1 variable
            config_0 = {unit_type: fixed_army}
            config_1 = {unit_type: enemy_count}
            
            batch_tasks = [(config_0.copy(), config_1.copy(), ai1_class, ai2_class) 
                          for _ in range(args.rounds)]
            
            futures = [executor.submit(_run_batch_battle, t) for t in batch_tasks]
            
            total_survivors_0 = 0
            total_survivors_1 = 0
            
            for f in concurrent.futures.as_completed(futures):
                result = f.result()
                total_survivors_0 += result["remaining_counts"][0]
                total_survivors_1 += result["remaining_counts"][1]
            
            # Moyenne des survivants
            avg_survivors_A = total_survivors_0 / args.rounds
            avg_survivors_B = total_survivors_1 / args.rounds
            
            y_survivors_A.append(avg_survivors_A)
            y_survivors_B.append(avg_survivors_B)
    
    print("\n[*] Génération du graphique Lanchester...")
    
    # Calcul de la courbe théorique de Lanchester (Square Law)
    # Survivants A = sqrt(N² - M²) si N > M, sinon 0
    # Survivants B = sqrt(M² - N²) si M > N, sinon 0
    N = fixed_army
    y_theory_A = []
    y_theory_B = []
    
    for M in x_enemy_counts:
        if N > M:
            y_theory_A.append(np.sqrt(N**2 - M**2))
            y_theory_B.append(0)
        elif M > N:
            y_theory_A.append(0)
            y_theory_B.append(np.sqrt(M**2 - N**2))
        else:
            y_theory_A.append(0)
            y_theory_B.append(0)
    
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle(f"Loi de Lanchester: {fixed_army} {unit_type} (A) vs Armée Croissante (B)", 
                 fontsize=14, fontweight='bold')
    
    # Courbes de simulation
    ax.plot(x_enemy_counts, y_survivors_A, 'b-', linewidth=2.5, markersize=5, 
            label=f'Survivants Armée A (simulation)', marker='o')
    ax.plot(x_enemy_counts, y_survivors_B, 'r-', linewidth=2.5, markersize=5, 
            label=f'Survivants Armée B (simulation)', marker='s')
    
    # Courbes théoriques (Lanchester)
    ax.plot(x_enemy_counts, y_theory_A, 'b--', linewidth=1.5, alpha=0.7, 
            label='Théorie Lanchester A')
    ax.plot(x_enemy_counts, y_theory_B, 'r--', linewidth=1.5, alpha=0.7, 
            label='Théorie Lanchester B')
    
    # Remplissage sous les courbes
    ax.fill_between(x_enemy_counts, y_survivors_A, alpha=0.2, color='blue')
    ax.fill_between(x_enemy_counts, y_survivors_B, alpha=0.2, color='red')
    
    # Ligne d'équilibre (N = M)
    ax.axvline(x=fixed_army, color='green', linestyle=':', linewidth=2, 
               label=f'Équilibre (N=M={fixed_army})')
    
    # Point d'intersection théorique
    ax.plot(fixed_army, 0, 'go', markersize=10, zorder=5)
    
    ax.set_xlabel(f"Taille de l'Armée B ({unit_type})", fontsize=12)
    ax.set_ylabel("Nombre de Survivants", fontsize=12)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(min_enemy, max_enemy)
    ax.set_ylim(0, max(max(y_survivors_A), max(y_survivors_B), fixed_army) * 1.1)
    
    # Annotation
    ax.annotate(f'Armée A fixe: {fixed_army}', xy=(min_enemy + 1, fixed_army * 0.95), 
                fontsize=10, color='blue')
    
    plt.tight_layout()
    
    # Sauvegarder dans statistiques/
    if not os.path.exists("statistiques"):
        os.makedirs("statistiques")
    
    filename = f"statistiques/lanchester_{args.ai1}_vs_{args.ai2}_{unit_type}.png"
    plt.savefig(filename, dpi=150)
    print(f"[*] Graphique sauvegardé: {filename}")
    
    # Afficher les statistiques
    print("\n" + "=" * 60)
    print("RÉSULTATS DE LA SIMULATION - LOI DE LANCHESTER")
    print("=" * 60)
    print(f"[*] Armée A (fixe): {fixed_army} {unit_type}")
    print(f"[*] Armée B (variable): {min_enemy} à {max_enemy} {unit_type}")
    
    # Trouver le point d'équilibre (où les deux courbes se croisent)
    for i, (a, b) in enumerate(zip(y_survivors_A, y_survivors_B)):
        if b >= a and i > 0:
            print(f"[*] Point de croisement: ~{x_enemy_counts[i]} unités ennemies")
            break
    
    print("=" * 60)
    
    # Sauvegarder le premier graphique
    plt.savefig(filename.replace('.png', '_survivants.png'), dpi=150)
    
    # === DEUXIÈME GRAPHIQUE : Évolution temporelle pour le dernier cas ===
    print("\n[*] Simulation détaillée du dernier cas avec évolution temporelle...")
    
    # Exécuter une bataille avec l'historique pour le dernier cas (max_enemy)
    config_0_final = {unit_type: fixed_army}
    config_1_final = {unit_type: max_enemy}
    
    final_result = run_headless_battle(
        config_0_final, config_1_final, 
        ai1_class, ai2_class, 
        max_turns=5000, width=40, height=30, 
        track_history=True
    )
    
    if "history" in final_result:
        history = final_result["history"]
        
        # Créer le graphique d'évolution temporelle
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        fig2.suptitle(f"Évolution au cours du temps: {fixed_army} vs {max_enemy} {unit_type}", 
                      fontsize=14, fontweight='bold')
        
        ax2.plot(history["turns"], history["team_0"], 'b-', linewidth=2, 
                 label=f'Armée A ({args.ai1})', marker='')
        ax2.plot(history["turns"], history["team_1"], 'r-', linewidth=2, 
                 label=f'Armée B ({args.ai2})', marker='')
        
        ax2.fill_between(history["turns"], history["team_0"], alpha=0.3, color='blue')
        ax2.fill_between(history["turns"], history["team_1"], alpha=0.3, color='red')
        
        ax2.set_xlabel("Tours", fontsize=12)
        ax2.set_ylabel("Nombre d'unités vivantes", fontsize=12)
        ax2.legend(loc='upper right', fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, max(history["turns"]))
        ax2.set_ylim(0, max(fixed_army, max_enemy) * 1.1)
        
        # Annotations
        ax2.axhline(y=fixed_army, color='blue', linestyle=':', alpha=0.5)
        ax2.axhline(y=max_enemy, color='red', linestyle=':', alpha=0.5)
        
        # Résultat
        winner_text = f"Vainqueur: {'Armée A' if final_result['winner'] == 0 else 'Armée B'}"
        ax2.annotate(winner_text, xy=(0.02, 0.02), xycoords='axes fraction', 
                     fontsize=12, fontweight='bold',
                     color='blue' if final_result['winner'] == 0 else 'red')
        
        plt.tight_layout()
        
        filename2 = f"statistiques/lanchester_{args.ai1}_vs_{args.ai2}_{unit_type}_evolution.png"
        plt.savefig(filename2, dpi=150)
        print(f"[*] Graphique d'évolution sauvegardé: {filename2}")
    
    plt.show()




# ═══════════════════════════════════════════════════════════════════════════════
# COMMANDE RUN : Lance une bataille unique entre deux IA
# Supporte le mode graphique et le mode terminal (curses)
# ═══════════════════════════════════════════════════════════════════════════════
def cmd_run(args):
    ai1_class = get_ai_class(args.ai1)
    ai2_class = get_ai_class(args.ai2)
    
    print(f"[*] Bataille: {args.ai1} vs {args.ai2}")
    
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
        print("[*] Mode terminal (curses)")
        import curses
        try:
            result = curses.wrapper(run_curses_battle, config_0, config_1, ai1_class, ai2_class)
        except curses.error as e:
            print(f"Erreur Curses: {e}")
            print("Note: Curses peut ne pas fonctionner correctement sous certains terminaux Windows sans 'windows-curses'.")
            return

        if result:
            winner_str = "Match Nul" if result["winner"] is None else f"Équipe {result['winner']}"
            print(f"\n[*] Résultat: {winner_str} en {result['turns']} tours")
            
            write_battle_report(result, args.ai1, args.ai2)
            print("[*] Rapport écrit dans statistiques/tournament_results.txt")
            
            if args.datafile:
                with open(args.datafile, "a", encoding="utf-8") as f:
                    f.write(f"{result}\n")
    else:
        run_graphical_battle(config_0, config_1, ai1_class, ai2_class)


# ═══════════════════════════════════════════════════════════════════════════════
# COMMANDE LOAD : Charge une sauvegarde existante et reprend la partie
# ═══════════════════════════════════════════════════════════════════════════════
def cmd_load(args):
    print(f"[*] Chargement de {args.savefile}")
    
    config_0 = {"Halberdier": 0, "Paladin": 0, "Arbalester": 0}
    config_1 = {"Halberdier": 0, "Paladin": 0, "Arbalester": 0}
    
    run_graphical_battle(config_0, config_1, ColonelSMART, MajorDaftSimple, load_file=args.savefile)


# ═══════════════════════════════════════════════════════════════════════════════
# COMMANDE TOURNEY : Lance un tournoi entre plusieurs IA
# Exécute tous les matchups possibles avec alternance des positions
# ═══════════════════════════════════════════════════════════════════════════════
def cmd_tourney(args):
    ai_classes = [get_ai_class(name) for name in args.ais]
    
    print(f"[*] Tournoi: {len(ai_classes)} IAs, {args.rounds} rounds")
    print(f"    IAs: {args.ais}")
    print(f"    Alternance positions: {not args.no_alternate}")
    
    results = {}
    config_0, config_1 = get_scenario_configs(args.scenario)
    
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
    print("[*] Tous les résultats sont dans statistiques/tournament_results.txt")


# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL : Parse les arguments et lance la commande appropriée
# Si aucune commande, lance le mode interactif graphique par défaut
# ═══════════════════════════════════════════════════════════════════════════════
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

5. LOI DE LANCHESTER (N fixe vs M croissant)
   python battle.py plot ColonelSMART MajorDaft --fixed 20 --range "range(1,30)" --unit Halberdier

6. CHARGER UNE SAUVEGARDE
   python battle.py load quicksave.dat

COMMANDES DISPONIBLES :
-----------------------
  run       Lancer une bataille unique
  tourney   Lancer un tournoi (plusieurs rounds)
  plot      Simuler la loi de Lanchester (graphique)
  load      Charger une sauvegarde existante

"""
    parser = argparse.ArgumentParser(
        prog="battle.py",
        description="Simulation de Bataille Médiévale - Outil Unifié",
        epilog=epilog_text,
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    run_parser = subparsers.add_parser("run", help="Lancer une bataille")
    run_parser.add_argument("ai1", help="IA équipe 0 (ex: ColonelSMART, MajorDaft)")
    run_parser.add_argument("ai2", help="IA équipe 1")
    run_parser.add_argument("-t", "--terminal", action="store_true",
                           help="Mode terminal (headless) au lieu de graphique")
    run_parser.add_argument("-S", "--scenario", type=str, default="Standard",
                           help="Scénario (Standard, Small, Duel, Archers, Horde)")
    run_parser.add_argument("-d", "--datafile", type=str, default=None,
                           help="Fichier où écrire les données")
    
    load_parser = subparsers.add_parser("load", help="Charger une sauvegarde")
    load_parser.add_argument("savefile", help="Fichier de sauvegarde")
    
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
    
    plot_parser = subparsers.add_parser("plot", help="Simuler la loi de Lanchester")
    plot_parser.add_argument("ai1", help="IA équipe 0 (armée fixe)")
    plot_parser.add_argument("ai2", help="IA équipe 1 (armée croissante)")
    plot_parser.add_argument("--unit", type=str, default="Halberdier",
                            help="Type d'unité (Halberdier, Paladin, Arbalester)")
    plot_parser.add_argument("--fixed", "-F", type=int, default=20,
                            help="Taille de l'armée fixe (équipe 0)")
    plot_parser.add_argument("--range", type=str, default="range(1,30)",
                            help="Plage armée ennemie: 'range(min,max)' ou 'min-max'")
    plot_parser.add_argument("-N", "--rounds", type=int, default=5,
                            help="Rounds par point de données")
    

    args = parser.parse_args()
    
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
