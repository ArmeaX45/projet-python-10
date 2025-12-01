# main.py
import time
import pygame
import curses

from src.map import map
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.arbalester import Arbalester
from src.ia_braindead import GeneralBrainDead
from src.ai_daft import MajorDaftSimple
# from src.game import Game   # pas nécessaire pour le test actuel


""" Youssef
def run_curses(stdscr, game: Game, ticks: int = 200, dt: float = 0.08):
    curses.curs_set(0)
    stdscr.nodelay(True)

    for _ in range(ticks):
        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q')):
            break

        game.logic_tick()

        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        title = "DAFT (J0) vs BRAINDEAD (J1) — q pour quitter"
        stdscr.addstr(0, 0, title[:max_x - 1])  # titre tronqué
        game.show_grid(stdscr)
        stdscr.refresh()
        curses.napms(int(dt * 1000))  # évite flicker, portable
"""


if __name__ == "__main__":
    # =========================
    # 1) Init pygame et la map
    # =========================
    pygame.init()

    m = map()  # ta classe map() n'a pas de paramètre "mamap.png"

    # Taille de fenêtre : si une image de fond existe, on prend sa taille
    if m.image:
        width, height = m.image.get_size()
    else:
        width, height = 800, 600

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Test DAFT vs BrainDead")

    # =========================
    # 2) Création des unités
    # =========================
    # DAFT contrôle l'équipe "A"
    h = Halberdier(0, 0)
    h.team = "A"

    # BrainDead contrôle l'équipe "B"
    p = Paladin(0, 4)
    p.team = "B"

    m.add_to_soldat_group(h)
    m.add_to_soldat_group(p)
    m.add_on_grid(h)
    m.add_on_grid(p)

    # =========================
    # 3) Instanciation des IA
    # =========================
    ia_daft = MajorDaftSimple(team_name="A")
    ia_brain = GeneralBrainDead(team_name="B")

    print("Position initiale sur la grille :")
    m.print_grid()

    clock = pygame.time.Clock()
    running = True
    tour = 0

    # =========================
    # 4) Boucle principale
    # =========================
    while running:
        clock.tick(5)  # 5 FPS pour voir les mouvements

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        tour += 1
        print(f"\n===== TOUR {tour} =====")

        # --- décisions des IA ---
        actions_daft = ia_daft.update(m)
        actions_brain = ia_brain.update(m)

        # --- exécution des actions ---
        all_actions = actions_daft + actions_brain

        for action in all_actions:
            name = action[0]

            if name == "attack":
                _, unit, target = action
                if getattr(target, "is_alive", False):
                    unit.attack(target)

            elif name == "move":
                _, unit, dx, dy = action
                unit.move(m, dx=dx, dy=dy)

        # --- reconstruire la grille ---
        m.grid = [['-' for _ in range(m.width)] for _ in range(m.height)]
        for u in m.all_soldats:
            if getattr(u, "is_alive", False):
                m.add_on_grid(u)

        # affichage terminal
        m.print_grid()

        # conditions de fin simples
        if not getattr(p, "is_alive", True):
            print("\n🎉 DAFT GAGNE (Paladin mort) !")
            running = False

        if not getattr(h, "is_alive", True):
            print("\n💀 BrainDead GAGNE (Halberdier mort) !")
            running = False

        # --- affichage pygame ---
        screen.fill((0, 0, 0))
        m.draw_map(screen)          # fond de carte si image
        m.all_soldats.draw(screen)  # sprites des unités
        pygame.display.flip()

    pygame.quit()


"""
if __name__ == "__main__":

    map = Map()

    halberdier = Halberdier(0,0)
    paladin = Paladin(10,1)
    arbalester = Arbalester(5,8)
    
    print(halberdier.instances)
    for soldat in halberdier.instances:
        map.add_to_soldat_group(soldat)
        map.add_on_grid(soldat)
    
    curses.wrapper(map.start_cmd)
    
    halberdier.move(map, dx=1)
    paladin.move(map, dy=1)
    arbalester.move(map, dy=-1)
    curses.wrapper(map.start_cmd)
"""

    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))

    # print("")
    # halberdier.attack(paladin)
    # print("")

    # print(str(halberdier))
    # print(str(paladin))
    # print(str(arbalester))

""" 
    for s in [h0, p1, a1]:
        game.add_to_soldat_group(s)
        game.add_on_grid(s)



game = Game()
    game.general_p0 = MajorDaft()        # Joueur 0 : DAFT
    game.general_p1 = CaptainBraindead() # Joueur 1 : BRAINDEAD

    # --- Place des unités (pense au owner) ---
    # Camp 0 (DAFT)
    h0 = Halberdier(0, 0);  h0.owner = 0
    # Camp 1 (BRAINDEAD)
    p1 = Paladin(11, 11);   p1.owner = 1
    a1 = Arbalester(5, 8);  a1.owner = 1
"""
if __name__ == "__main__":
    # ==== Bataille avec plusieurs troupes : DAFT (A) vs BrainDead (B) ====

    m = map()

    # ---------- Troupes de DAFT : équipe A ----------
    allies = []
    # 5 Halberdiers en colonne à gauche : x = 0, y = 0,2,4,6,8
    for i in range(5):
        h = Halberdier(0, i * 2)
        h.team = "A"
        allies.append(h)
        m.add_to_soldat_group(h)
        m.add_on_grid(h)

    # ---------- Troupes de BrainDead : équipe B ----------
    enemies = []
    # 5 Paladins en colonne à droite : x = 10, y = 0,2,4,6,8
    for i in range(5):
        p = Paladin(10, i * 2)
        p.team = "B"
        enemies.append(p)
        m.add_to_soldat_group(p)
        m.add_on_grid(p)

    # ---------- IA ----------
    ia_daft = MajorDaftSimple(team_name="A")
    ia_brain = GeneralBrainDead(team_name="B")

    print("=== POSITION INITIALE ===")
    m.print_grid()

    MAX_TURNS = 20

    for turn in range(1, MAX_TURNS + 1):
        print(f"\n===== TOUR {turn} =====")

        # Décisions IA
        actions_daft = ia_daft.update(m)
        actions_brain = ia_brain.update(m)

        print("Actions DAFT :")
        for act in actions_daft:
            print("  ", act)

        print("Actions BrainDead :")
        for act in actions_brain:
            print("  ", act)

        # Exécution des actions
        all_actions = actions_daft + actions_brain

        for action in all_actions:
            name = action[0]

            if name == "move":
                _, unit, dx, dy = action
                unit.move(m, dx=dx, dy=dy)

            elif name == "attack":
                _, unit, target = action
                if getattr(target, "is_alive", False):
                    unit.attack(target)

        # Reconstruire la grille
        m.grid = [['-' for _ in range(m.width)] for _ in range(m.height)]
        for u in m.all_soldats:
            if getattr(u, "is_alive", False):
                m.add_on_grid(u)

        m.print_grid()

        # Vérifier qui est encore vivant
        alive_A = [u for u in m.all_soldats if getattr(u, "team", None) == "A" and getattr(u, "is_alive", False)]
        alive_B = [u for u in m.all_soldats if getattr(u, "team", None) == "B" and getattr(u, "is_alive", False)]

        if not alive_A:
            print("\n💀 Tous les soldats de DAFT (A) sont morts. BrainDead (B) gagne.")
            break

        if not alive_B:
            print("\n🎉 Tous les soldats de BrainDead (B) sont morts. DAFT (A) gagne.")
            break

    print("\n=== FIN DE LA BATAILLE ===")

