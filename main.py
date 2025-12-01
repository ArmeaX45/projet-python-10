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


# ============================================================
#                      BLOC PRINCIPAL UNIQUE
# ============================================================

if __name__ == "__main__":

    # =========================
    # 1) Init pygame et la map
    # =========================
    pygame.init()

    m = map()  # utilise mamap.png automatiquement

    # Dimension fenêtre = dimension image
    if m.image:
        width, height = m.image.get_size()
    else:
        width, height = 800, 600

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("DAFT vs BrainDead - Battle Simulation")


    # =========================
    # 2) Création des troupes
    # =========================

    # --- Équipe A (DAFT) : 5 halberdiers à gauche ---
    for i in range(5):
        h = Halberdier(1, 1 + i * 2)
        h.team = "A"
        m.add_to_soldat_group(h)
        m.add_on_grid(h)

    # --- Équipe B (BrainDead) : 5 paladins à droite ---
    for i in range(5):
        p = Paladin(10, 1 + i * 2)
        p.team = "B"
        m.add_to_soldat_group(p)
        m.add_on_grid(p)


    # =========================
    # 3) IA
    # =========================
    ia_daft = MajorDaftSimple(team_name="A")
    ia_brain = GeneralBrainDead(team_name="B")

    print("=== POSITION INITIALE ===")
    m.print_grid()

    clock = pygame.time.Clock()
    running = True
    MAX_TURNS = 50
    turn = 0


    # =========================
    # 4) Boucle principale
    # =========================
    while running:
        turn += 1
        print(f"\n===== TOUR {turn} =====")

        clock.tick(3)  # ralentir la simulation pour voir le mouvement

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- décisions IA ---
        actions_A = ia_daft.update(m)
        actions_B = ia_brain.update(m)
        all_actions = actions_A + actions_B

        # --- exécution ---
        for action in all_actions:
            if action[0] == "move":
                _, unit, dx, dy = action
                unit.move(m, dx=dx, dy=dy)

            elif action[0] == "attack":
                _, unit, target = action
                if getattr(target, "is_alive", False):
                    unit.attack(target)

        # --- reconstruire la grille ---
        m.grid = [['-' for _ in range(m.width)] for _ in range(m.height)]
        for u in m.all_soldats:
            if getattr(u, "is_alive", False):
                m.add_on_grid(u)

        m.print_grid()  # affichage console ASCII

        # --- affichage pygame ---
        screen.fill((0, 0, 0))
        m.draw_map(screen)
        m.all_soldats.draw(screen)
        pygame.display.flip()

        # --- conditions de fin ---
        alive_A = [s for s in m.all_soldats if getattr(s, "team", None) == "A" and s.is_alive]
        alive_B = [s for s in m.all_soldats if getattr(s, "team", None) == "B" and s.is_alive]

        if not alive_A:
            print("\n💀 BrainDead (B) gagne !")
            running = False
        if not alive_B:
            print("\n🎉 DAFT (A) gagne !")
            running = False
        if turn >= MAX_TURNS:
            print("\n⏳ Temps écoulé ! Match nul.")
            running = False

    pygame.quit()


