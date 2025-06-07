import pandas as pd

fichier_excel = "Bac_Benin_2019_2023.xlsx"

# Charger les noms des feuilles
feuilles = pd.ExcelFile(fichier_excel).sheet_names
print("Feuilles disponibles :", feuilles)

# Charger chaque feuille
df_par_serie = pd.read_excel(fichier_excel, sheet_name=feuilles[0])
df_par_departement = pd.read_excel(fichier_excel, sheet_name=feuilles[1])

# Enregistrer en CSV
df_par_serie.to_csv("bac_benin_par_serie.csv", index=False)
df_par_departement.to_csv("bac_benin_par_departement.csv", index=False)

print("Conversion terminée. Deux fichiers CSV sont créés.")
