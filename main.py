# main.py
import time
import curses
import pygame
from src.map import map as GameMap
from src.halberdier import Halberdier
from src.paladin import Paladin
from src.ia_braindead import GeneralBrainDead

def main():
    pygame.init()

    # === NOUVEAU : création de la fenêtre ===
    # Taille de la fenêtre ; adapte à la taille de ton image de fond si besoin
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("MedievAIl BAIttle - Test IA")

    # Création de la map
    m = GameMap()

    # Création des unités
    h = Halberdier(1, 0)
    h.team = "A"
    p = Paladin(5, 0)
    p.team = "B"

    # Ajout sur la map
    m.add_to_soldat_group(h)
    m.add_to_soldat_group(p)
    m.add_on_grid(h)
    m.add_on_grid(p)

    # IA pour chaque équipe
    ia_A = GeneralBrainDead(team_name="A")
    ia_B = GeneralBrainDead(team_name="B")

    clock = pygame.time.Clock()
    running = True

    while running:
        # 1) Gestion des événements (fermeture fenêtre, etc.)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2) Appel des IA
        actions_A = ia_A.update(m)
        actions_B = ia_B.update(m)

        # 3) Application des actions (A puis B, par exemple)
        for act in actions_A + actions_B:
            if act[0] == "attack":
                _, unit, target = act
                if unit.is_alive and target.is_alive:
                    unit.attack(target)
            elif act[0] == "move":
                _, unit, dx, dy = act
                if unit.is_alive:
                    unit.move(m, dx, dy)

        # 4) Nettoyer les morts
        for s in list(m.all_soldats):
            if not s.is_alive:
                gx = s.rect.x // s.rect.width
                gy = s.rect.y // s.rect.height
                if 0 <= gy < m.height and 0 <= gx < m.width:
                    m.grid[gy][gx] = '-'
                m.all_soldats.remove(s)

        # 5) Affichage
        screen.fill((0, 0, 0))  # fond noir
        m.draw(screen)          # utilise ta méthode draw de map.py
        pygame.display.flip()

        # 6) Limiter la vitesse (par exemple 5 tours/seconde pour bien voir)
        clock.tick(5)

    pygame.quit()

if __name__ == "__main__":
    main()