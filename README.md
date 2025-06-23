# 🖥️ Windows Info Script

Un script Python interactif pour collecter, afficher et enregistrer les informations système essentielles d’un PC Windows. Idéal pour l’inventaire informatique, le diagnostic ou la préparation à la migration Windows 11.

---

## 📦 Fonctionnalités

- Interface en ligne de commande claire et interactive
- Saisie du nom de l’utilisateur et d’une information personnalisée (ex : service, usage…)
- Récupération automatique :
  - Nom du poste
  - Fabricant, modèle, numéro de série
  - Date de mise en service de Windows
  - Processeur, RAM, stockage
  - Version de Windows
  - Compatibilité Windows 11 (analyse détaillée)
- Résumé lisible à l’écran
- Enregistrement optionnel dans `rapport_pc.txt` (avec gestion du doublon)
- Boucle permettant l’analyse de plusieurs postes
- Vérification des droits administrateur
- Gestion des erreurs simple et propre
- Rapport au format texte tabulé (compatible Excel)

---

## 🚀 Utilisation

1. **Lancer le script** (double-clic ou terminal) :
   ```bash
   python windows_info.py
