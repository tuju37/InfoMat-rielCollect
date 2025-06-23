# 🖥️ Windows Info Script

Un script Python interactif pour collecter, afficher et enregistrer les informations système essentielles d’un PC Windows. Idéal pour l’inventaire informatique, le diagnostic ou la préparation à la migration Windows 11.

---
## Transférable sur clé USB
---
- Attention à la fiabilité de la compatibilité Windows 11. ⚠
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
  - ⚠ Compatibilité Windows 11 (analyse détaillée)
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
   @echo off.bat

## 📂 Emplacement du fichier de rapport

Le fichier `rapport_pc.txt` sera créé automatiquement **lors de la première sauvegarde d’un PC** effectuée avec le script.

### Chemin par défaut :
```bash
 ...\InfoMaterielCollect\windows_info\rapport_pc.txt
```
---
## 📋 Informations collectées par le script

| N° | Champ                          | Description                                                                 |
|----|--------------------------------|-----------------------------------------------------------------------------|
| 1  | **Nom**                        | Nom de la personne utilisant l’ordinateur (saisi manuellement)             |
| 2  | **Nom de l’appareil**          | Nom du PC sur le réseau (hostname)                                         |
| 3  | **Détails / Info**             | Info personnalisée (ex : service, salle, usage…)                           |
| 4  | **Marque du PC**               | Constructeur (ex : Dell, HP, Lenovo…)                                      |
| 5  | **Modèle / Référence**         | Modèle exact de l’ordinateur                                               |
| 6  | **Numéro de série**            | Numéro de série unique du matériel                                         |
| 7  | **Mise en service**            | Date d’installation initiale de Windows                                    |
| 8  | **RAM (Go)**                   | Quantité de mémoire vive installée (en Go)                                 |
| 9  | **Stockage**                   | Capacité du disque principal                                               |
| 10 | **Processeur**                 | Modèle du processeur (ex : Intel Core i5…)                                 |
| 11 | **⚠Compatible Windows 11 ?**    | Oui / Non + détails (ex : TPM, Secure Boot, CPU…)                          |
| 12 | **Date de test**              | Date à laquelle l’analyse a été effectuée                                  |

