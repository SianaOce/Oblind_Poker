import os
from pathlib import Path

# Dossier pour l'enregistrement des donnees utilisateur (jetons,joueurs,...)
CONFIG_DIR = os.path.join(Path.home(), ".configMTPoker")

# Valeurs sélectionnables des blinds/surblinds
SB_BB = ["1 / 2", "2 / 4", "3 / 6", "4 / 8",
         "5 / 10", "6 / 12", "10 / 20", "15 / 30", "20 / 40", "25 / 50",
         "30 / 60", "50 / 100", "75 / 150", "100 / 200", "150 / 300", "200 / 400",
         "250 / 500", "300 / 600", "400 / 800", "500 / 1000", "750 / 1500", "1000 / 2000",
         "1500 / 3000", "2000 / 4000", "3000 / 6000", "4000 / 8000", "5000 / 10000"]

# Valeurs sélectionnables des antes
ANTES = ["", "1", "2", "3", "4", "5", "10", "15", "20", "25", "50", "75", "100", "150", "200", "250", "400",
         "500", "750", "1000", "1500", "2000"]

# Valeurs sélectionnables des temps par niveau
TIME_SPAN = ["", "0:10", "0:15", "0:20", "0:30", "0:45", "1:00", "1:15", "1:30", "1:45", "2:00", "2:30", "3:00"]

# Valeurs sélectionnables des valeurs des jetons
VALUE = ["1", "2", "5", "10", "25", "50", "100", "500", "1000"]
