import platform
import socket
import getpass
import subprocess
import os
import sys
from datetime import datetime
import threading

try:
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
except Exception:
    pass

RAPPORT_FILENAME = "rapport_pc.txt"
_report_lock = threading.Lock()

def log_error(msg):
    print(f"[ERREUR] {msg}", file=sys.stderr)

def clear_console():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        pass

def is_admin():
    if sys.platform == "win32":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    return hasattr(os, "geteuid") and os.geteuid() == 0

def elevate_if_needed():
    if sys.platform == "win32" and not is_admin():
        print("Ce script nécessite les droits administrateur pour fonctionner correctement.")
        try:
            import ctypes
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
            sys.exit(0)
        except Exception as e:
            log_error(f"Élévation échouée : {e}")
            print("Impossible d'obtenir les droits administrateur. Arrêt du script.")
            sys.exit(1)

def get_windows_info_dir():
    wininfo_dir = os.environ.get("WININFO_DIR")
    if wininfo_dir and os.path.isdir(wininfo_dir):
        return wininfo_dir
    return os.getcwd()

def get_wmic_value(property, alias):
    try:
        result = subprocess.check_output(
            f'chcp 437 >nul && wmic {property} get {alias} /value', shell=True,
            stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
        ).decode('utf-8', errors='ignore')
        for line in result.splitlines():
            if "=" in line:
                key, val = line.split("=", 1)
                if key.strip().lower() == alias.lower():
                    return val.strip()
    except Exception as e:
        log_error(f"Accès WMIC ({property}, {alias}): {e}")
    return ""

def get_windows_install_date():
    try:
        result = subprocess.check_output(
            'wmic os get InstallDate /value', shell=True,
            stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
        ).decode('utf-8', errors='ignore')
        for line in result.splitlines():
            if line.startswith("InstallDate="):
                date_str = line.split("=", 1)[1].strip()
                if len(date_str) >= 8:
                    return datetime.strptime(date_str[:8], "%Y%m%d").strftime("%d/%m/%Y")
    except Exception as e:
        log_error(f"Récupération de la date d'installation de Windows : {e}")
    return ""

def get_ram_gb():
    try:
        result = subprocess.check_output(
            'wmic computersystem get TotalPhysicalMemory', shell=True,
            stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
        ).decode('utf-8', errors='ignore').splitlines()
        for line in result:
            line = line.strip()
            if line.isdigit():
                return str(round(int(line) / (1024**3)))
    except Exception as e:
        log_error(f"Récupération de la RAM : {e}")
    return ""

def get_storage():
    try:
        result = subprocess.check_output(
            'wmic logicaldisk where "drivetype=3" get size', shell=True,
            stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
        ).decode('utf-8', errors='ignore').splitlines()
        sizes = [int(line.strip()) for line in result if line.strip().isdigit()]
        if sizes:
            return f"{str(round(sum(sizes) / (1024**3)))} Go"
    except Exception as e:
        log_error(f"Récupération du stockage : {e}")
    return ""

def get_windows_version():
    try:
        version = platform.release()
        return version if version in ("10", "11") else version
    except Exception as e:
        log_error(f"Détection de la version de Windows : {e}")
        return ""

def get_tpm_version():
    try:
        result = subprocess.check_output(
            'wmic /namespace:\\\\root\\CIMV2\\Security\\MicrosoftTpm path Win32_Tpm get SpecVersion /value',
            shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
        ).decode('utf-8', errors='ignore')
        for line in result.splitlines():
            if "SpecVersion=" in line:
                version = line.split("=", 1)[1].strip()
                if version:
                    return version.split(",")[0]
    except Exception:
        pass
    return ""

def is_cpu_compatible():
    try:
        cpu_name = get_wmic_value('cpu', 'Name').lower()
        cpu_ok_keywords = [
            "intel core i3-8", "intel core i5-8", "intel core i7-8", "intel core i9-8",
            "intel core i3-9", "intel core i5-9", "intel core i7-9", "intel core i9-9",
            "intel core i3-10", "intel core i5-10", "intel core i7-10", "intel core i9-10",
            "intel core i3-11", "intel core i5-11", "intel core i7-11", "intel core i9-11",
            "amd ryzen 3", "amd ryzen 5", "amd ryzen 7", "amd ryzen 9", "amd ryzen 5 pro", "amd ryzen 7 pro", "amd ryzen 9 pro",
            "amd ryzen threadripper", "amd ryzen 7 3700x", "amd ryzen 5 3600", "amd ryzen 5 5600x", "amd ryzen 7 5800x"
        ]
        return any(kw in cpu_name for kw in cpu_ok_keywords)
    except Exception:
        return False

def check_windows11_compatibility():
    """Vérifie la compatibilité avec Windows 11 en effectuant des recherches approfondies pour chaque composant."""
    try:
        # Vérification de la RAM
        ram = get_ram_gb()
        ram_ok = int(ram) >= 4 if ram and ram.isdigit() else False

        # Vérification du CPU (nombre de cœurs et compatibilité)
        cpu_ok = False
        try:
            cores = int(get_wmic_value('cpu', 'NumberOfCores'))
            cpu_ok = cores >= 2
        except Exception:
            pass

        cpu_name = get_wmic_value('cpu', 'Name').lower()
        cpu_compatible = any(keyword in cpu_name for keyword in [
            "intel core i3-8", "intel core i5-8", "intel core i7-8", "intel core i9-8",
            "intel core i3-9", "intel core i5-9", "intel core i7-9", "intel core i9-9",
            "intel core i3-10", "intel core i5-10", "intel core i7-10", "intel core i9-10",
            "intel core i3-11", "intel core i5-11", "intel core i7-11", "intel core i9-11",
            "amd ryzen 3", "amd ryzen 5", "amd ryzen 7", "amd ryzen 9", "amd ryzen 5 pro", "amd ryzen 7 pro", "amd ryzen 9 pro",
            "amd ryzen threadripper", "amd ryzen 7 3700x", "amd ryzen 5 3600", "amd ryzen 5 5600x", "amd ryzen 7 5800x"
        ])

        # Vérification de l'architecture CPU
        arch = platform.machine()
        cpu_arch_ok = arch in ("AMD64", "x86_64", "ARM64")

        # Vérification du stockage
        storage_ok = False
        try:
            storage_gb = int(get_storage().split()[0])
            storage_ok = storage_gb >= 64
        except Exception:
            pass

        # Vérification du TPM (Trusted Platform Module)
        tpm_version = get_tpm_version()
        tpm_ok = tpm_version.startswith("2")

        # Vérification du Secure Boot
        secure_boot_ok = get_wmic_value('computersystem', 'SecureBootState') == "1"

        # Résumé de la compatibilité
        return {
            "RAM >= 4Go": ram_ok,
            "CPU >= 2 cœurs": cpu_ok,
            "CPU 64 bits": cpu_arch_ok,
            "Stockage >= 64Go": storage_ok,
            "TPM 2.0": tpm_ok,
            "TPM version": tpm_version or "Absent",
            "Secure Boot": secure_boot_ok,
            "Processeur compatible": cpu_compatible,
            "Compatible Windows 11": all([ram_ok, cpu_ok, cpu_arch_ok, storage_ok, tpm_ok, secure_boot_ok, cpu_compatible])
        }
    except Exception as e:
        log_error(f"Erreur lors de la vérification de compatibilité : {e}")
        return {}

def afficher_details_compatibilite(compat):
    """Affiche le détail de la compatibilité Windows 11 de façon claire et concise."""
    try:
        print("\nDétail compatibilité Windows 11 :")
        for k, v in compat.items():
            if k == "Compatible Windows 11":
                continue
            msg = "OK" if v else "NON"
            if k == "TPM 2.0" and not v:
                msg += " (TPM absent ou version < 2.0)"
            elif k == "Processeur compatible" and not v:
                msg += " (Processeur non listé compatible Windows 11)"
            elif k == "Secure Boot" and not v:
                msg += " (Peut être activé dans le BIOS/UEFI si supporté)"
            print(f"  {k:<25}: {msg}")
        print(f"\nRésultat global : {'OUI' if compat['Compatible Windows 11'] else 'NON'}")
    except Exception as e:
        log_error(f"Affichage compatibilité : {e}")

def choisir_service():
    """Affiche une liste de services et retourne le choix de l'utilisateur."""
    services = [
        "Autres"
    ]
    print("\nSélectionnez le service correspondant à ce poste :")
    for i, s in enumerate(services, 1):
        print(f"{i}. {s}")
    while True:
        choix = safe_input("Numéro du service : ").strip()
        if choix.isdigit() and 1 <= int(choix) <= len(services):
            if services[int(choix)-1] == "Autres":
                autre = safe_input("Veuillez préciser le service : ").strip()
                return autre if autre else "Autres"
            return services[int(choix)-1]
        print("Choix invalide, recommencez.")

def afficher_details_compatibilite(compat):
    """Affiche le détail de la compatibilité Windows 11 de façon claire."""
    try:
        print("\nDétail compatibilité Windows 11 :")
        for k, v in compat.items():
            if k == "Compatible Windows 11":
                continue
            if k == "TPM version":
                print(f"  {k:<25}: {v}")
                continue
            if v:
                msg = "OK"
            else:
                if k == "TPM 2.0":
                    msg = "NON (TPM absent ou version < 2.0)"
                elif k == "Processeur compatible":
                    msg = "NON (Processeur non listé compatible Windows 11)"
                elif k == "Secure Boot":
                    msg = "NON (Peut être activé dans le BIOS/UEFI si supporté)"
                else:
                    msg = "NON"
            print(f"  {k:<25}: {msg}")
        print(f"\nRésultat global : {'OUI' if compat['Compatible Windows 11'] else 'NON'}")
    except Exception as e:
        log_error(f"Affichage compatibilité : {e}")

def resume_rapide(infos, compat, details):
    """Affiche un résumé rapide des informations principales de façon claire."""
    try:
        print("\n" + "="*60)
        print("Résumé rapide :")
        print(f"Utilisateur           : {infos['Nom']}")
        print(f"Nom de l'appareil     : {infos['Nom de l\'appareil']}")
        print(f"Service               : {infos['Service']}")
        print(f"Marque du PC          : {infos['Marque du PC']}")
        print(f"Modèle / Référence    : {infos['Modèle / Référence']}")
        print(f"Numéro de série       : {infos['Numéro de série']}")
        print(f"Mise en service       : {infos['Mise en service']}")
        print(f"RAM (Go)              : {infos['RAM (Go)']}")
        print(f"Stockage              : {infos['Stockage']}")
        print(f"Processeur            : {infos['Processeur']}")
        print(f"Windows               : {infos['Windows']}")
        print(f"Compatible Windows 11 : {infos['Compatible Windows 11 ?']}{details}")
        print("="*60)
    except Exception as e:
        log_error(f"Affichage résumé : {e}")

def safe_input(prompt):
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\nArrêt demandé par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        log_error(f"Saisie utilisateur : {e}")
        sys.exit(1)

def write_report_threadsafe(txt_path, colonnes, valeurs):
    with _report_lock:
        write_header = not os.path.exists(txt_path) or os.path.getsize(txt_path) == 0
        try:
            with open(txt_path, "a", encoding="utf-8") as f:
                if write_header:
                    f.write("\t".join(colonnes) + "\n")
                f.write("\t".join(valeurs) + "\n")
        except Exception as e:
            log_error(f"Écriture du rapport : {e}")
            raise

def creer_raccourci_rapport(txt_path):
    return

def creer_raccourci_script():
    return

def main():
    while True:
        try:
            clear_console()
            print("="*60)
            print("           Informations sur ce PC Windows")
            print("="*60)

            # Demande le nom de l'utilisateur
            utilisateur = safe_input("Entrez le nom de la personne qui utilise cet ordinateur : ").strip()

            try:
                if sys.platform == "win32":
                    import ctypes
                    from ctypes import wintypes
                    WTS_CURRENT_SERVER_HANDLE = 0
                    WTS_CURRENT_SESSION = -1
                    WTSQuerySessionInformation = ctypes.windll.Wtsapi32.WTSQuerySessionInformationW
                    WTSFreeMemory = ctypes.windll.Wtsapi32.WTSFreeMemory
                    info = ctypes.c_void_p()
                    bytes_returned = wintypes.DWORD()
                    username = None
                    if WTSQuerySessionInformation(WTS_CURRENT_SERVER_HANDLE, WTS_CURRENT_SESSION, 5, ctypes.byref(info), ctypes.byref(bytes_returned)):
                        username = ctypes.wstring_at(info)
                        WTSFreeMemory(info)
                    session_user = username if username else os.environ.get("USERNAME") or getpass.getuser()
                else:
                    session_user = os.environ.get("USERNAME") or getpass.getuser()
            except Exception:
                session_user = os.environ.get("USERNAME") or getpass.getuser()
            hostname = socket.gethostname()
            print(f"Session utilisateur : {session_user}")
            print(f"Nom de l'appareil : {hostname}")
            service_choisi = choisir_service()
            infos = {
                "Nom": utilisateur,  # Utilise le nom saisi par l'utilisateur
                "Nom de l'appareil": hostname,
                "Service": service_choisi,
                "Marque du PC": get_wmic_value('computersystem', 'Manufacturer'),
                "Modèle / Référence": get_wmic_value('computersystem', 'Model'),
                "Numéro de série": get_wmic_value('bios', 'SerialNumber'),
                "Mise en service": get_windows_install_date(),
                "RAM (Go)": get_ram_gb(),
                "Stockage": get_storage(),
                "Processeur": get_wmic_value('cpu', 'Name'),
                "Windows": "",
                "Compatible Windows 11 ?": "",
                "Date de test": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            version_windows = get_windows_version()
            infos["Windows"] = version_windows if version_windows else "Inconnu"
            compat = check_windows11_compatibility()
            if version_windows == "11":
                infos["Compatible Windows 11 ?"] = ""
            else:
                infos["Compatible Windows 11 ?"] = "OUI" if compat["Compatible Windows 11"] else "NON"
            details = ""
            if infos["Compatible Windows 11 ?"] == "NON":
                details_list = [k for k, v in compat.items() if k != "Compatible Windows 11" and not v]
                if details_list:
                    details = " (Non compatible : " + ", ".join(details_list) + ")"
            resume_rapide(infos, compat, details)
            print("\nRésumé du rapport :")
            for k in [
                "Nom", "Nom de l'appareil", "Service", "Marque du PC", "Modèle / Référence", "Numéro de série",
                "Mise en service", "RAM (Go)", "Stockage", "Processeur", "Windows", "Compatible Windows 11 ?"
            ]:
                print(f"{k:<25}: {infos.get(k, '')}{details if k == 'Compatible Windows 11 ?' else ''}")
            afficher_details_compatibilite(compat)
            print("="*60)
            txt_path = os.path.join(get_windows_info_dir(), RAPPORT_FILENAME)
            colonnes = [
                "N°", "Nom", "Nom de l'appareil", "Service", "Marque du PC", "Modèle / Référence", "Numéro de série",
                "Mise en service", "RAM (Go)", "Stockage", "Processeur", "Windows", "Compatible Windows 11 ?", "Date de test"
            ]
            deja_present = False
            lignes = []
            if os.path.exists(txt_path):
                try:
                    with open(txt_path, "r", encoding="utf-8") as f:
                        lignes = f.readlines()
                        for ligne in lignes[1:]:
                            champs = ligne.strip().split("\t")
                            if len(champs) >= 7 and champs[1] == infos["Nom"] and champs[5] == infos["Numéro de série"]:
                                deja_present = True
                                break
                except Exception as e:
                    log_error(f"Lecture du fichier rapport_pc.txt : {e}")
                    lignes = []
            if deja_present:
                print("Ce PC est déjà présent dans le fichier rapport_pc.txt, rien n'a été ajouté.")
            else:
                numero = 1
                for ligne in lignes[1:]:
                    if ligne.strip() and not ligne.startswith("#") and not ligne.startswith("-"):
                        numero += 1
                valeurs = [
                    str(numero),  # Ajoute le numéro de l'ordinateur
                    infos.get("Nom", ""),
                    infos.get("Nom de l'appareil", ""),
                    infos.get("Service", ""),
                    infos.get("Marque du PC", ""),
                    infos.get("Modèle / Référence", ""),
                    infos.get("Numéro de série", ""),
                    infos.get("Mise en service", ""),
                    infos.get("RAM (Go)", ""),
                    infos.get("Stockage", ""),
                    infos.get("Processeur", ""),
                    infos.get("Windows", ""),
                    infos.get("Compatible Windows 11 ?","") + details,
                    infos.get("Date de test", "")
                ]
                enregistrer = safe_input("Voulez-vous enregistrer ce PC dans le fichier texte ? (O/N) : ").strip().lower()
                if enregistrer == "o":
                    try:
                        write_report_threadsafe(txt_path, colonnes, valeurs)
                        print(f"Un rapport a été ajouté à : {txt_path}")
                        creer_raccourci_rapport(txt_path)
                    except Exception as e:
                        log_error(f"Erreur lors de l'ajout du rapport : {e}")
                        continue
                else:
                    print("Ce PC n'a pas été enregistré. Le fichier texte existant reste inchangé.")
            print()
            relancer = safe_input("Voulez-vous analyser un autre poste ? (O/N) : ").strip().lower()
            if relancer != "o":
                break
        except Exception as e:
            log_error(f"Inattendu : {e}")
            safe_input("Appuyez sur Entrée pour réessayer ou Ctrl+C pour quitter...")

if __name__ == "__main__":
    elevate_if_needed()
    main()
    safe_input("Appuyez sur Entrée pour fermer...")
