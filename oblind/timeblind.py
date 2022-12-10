from oblind.constants import TIME_SPAN, SB_BB, ANTES


# Fonction pour trier les niveaux de SB/BB dans l'ordre croissant et retourner la liste des niveau et leur nombre
def sort_sb_bb(levels):
    n = 0
    for i in range(0, 9):
        if levels[i][0] != 0:
            n += 1
            if levels[i][1] > levels[i + 1][1] and levels[i + 1][0] != 0:
                levels[i + 1][1] = levels[i][1]
        elif levels[i][0] == 0:
            levels[i][1] = 0
            levels[i + 1][0] = 0
    return levels, n


# Fonction pour retourner un dictionnaire avec :
#               les niveaux de SB/BB/Ante et leur durée, le nombre de niveau, le temps total
# cle => lvl_n, valeur => (int(min),str(SB/BB),str(Ante))
# cle => Nb_lvl, valeur => int(nb niveau)
# cle => Tps_Tot, valeur => int(min)
def game_structure(levels):
    l_g = 0
    structure = {}
    for i in range(0, 10):
        if TIME_SPAN[levels[i][0]] != "":
            text = TIME_SPAN[levels[i][0]].split(":")
            structure[f"lvl_{i + 1}"] = [60 * int(text[0].strip()) + int(text[1].strip()),
                                         SB_BB[levels[i][1] + (i - 1)], ANTES[levels[i][2]]]
            l_g += 60 * int(text[0].strip()) + int(text[1].strip())

    structure["Nb_Lvl"] = len(structure)
    structure["Tps_Tot"] = l_g

    return structure
