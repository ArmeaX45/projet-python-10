import pickle
import os

def generate_battle_report(save_filename="quicksave.dat"):
    filepath = os.path.join("saves", save_filename)
    
    if not os.path.exists(filepath):
        print(f"Erreur : {save_filename} introuvable.")
        return

    try:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        
        units = data["units"]
        
        # --- CALCUL DES STATISTIQUES ---
        team_0_survivors = [u for u in units if u.team == 0 and u.hp > 0]
        team_1_survivors = [u for u in units if u.team == 1 and u.hp > 0]
        
        hp_total_0 = sum([u.hp for u in team_0_survivors])
        hp_total_1 = sum([u.hp for u in team_1_survivors])

        # --- CRÉATION DU RAPPORT LISIBLE ---
        report = f"""
        ======= RAPPORT DE BATAILLE : {save_filename} =======
        Équipe 0 (DAFT) : {len(team_0_survivors)} survivants | PV Totaux: {hp_total_0}
        Équipe 1 (BRAIN) : {len(team_1_survivors)} survivants | PV Totaux: {hp_total_1}
        ----------------------------------------------------
        GAGNANT : {'Équipe 0' if hp_total_0 > hp_total_1 else 'Équipe 1'}
        ====================================================
        """
        
        # Sauvegarde du rapport en format texte (lisible par toi)
        with open("battle_report.txt", "w", encoding="utf-8") as f_out:
            f_out.write(report)
            
        print("[*] Rapport statistique généré dans 'battle_report.txt'")
        
    except Exception as e:
        print(f"Erreur lors de l'analyse : {e}")

import pickle
import os

def check_end_and_report(game):
    """Vérifie si la bataille est finie et génère les stats."""
    allies = [u for u in game.all_soldats if u.team == 0 and u.is_alive]
    enemies = [u for u in game.all_soldats if u.team == 1 and u.is_alive]

    # Si une équipe est décimée
    if len(allies) == 0 or len(enemies) == 0:
        winner = "Équipe 0 (DAFT)" if len(allies) > 0 else "Équipe 1 (BRAIN)"
        if len(allies) == 0 and len(enemies) == 0: winner = "Égalité (Match Nul)"

        report = f"""
        ========= FIN DE LA BATAILLE =========
        VAINQUEUR : {winner}
        Unités restantes Équipe 0 : {len(allies)}
        Unités restantes Équipe 1 : {len(enemies)}
        Points de Vie Totaux 0 : {sum(u.hp for u in allies)}
        Points de Vie Totaux 1 : {sum(u.hp for u in enemies)}
        ======================================
        """
        
        # On écrit le fichier texte lisible pour tes stats
        with open("tournament_results.txt", "a", encoding="utf-8") as f:
            f.write(report + "\n")
        
        print("[*] La bataille est finie. Rapport généré dans 'tournament_results.txt'")
        return True # La bataille est terminée
    return False # La bataille continue