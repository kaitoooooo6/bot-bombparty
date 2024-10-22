import pyautogui
import pyperclip
import time
import threading
import tkinter as tk
import keyboard
import pytesseract  # Module OCR pour extraire du texte des images
from PIL import ImageGrab, Image  # Pour capturer l'écran
import datetime  # Pour les logs avec timestamps

# Initialiser le chemin pour Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Mettre à jour avec le chemin absolu vers votre fichier mots.txt
chemin_fichier_mots = r'E:\python\bot boum\mots.txt'

# Charger la liste de mots
try:
    with open(chemin_fichier_mots, 'r', encoding='utf-8') as file:
        mots = file.read().splitlines()
        print(f"Nombre de mots chargés : {len(mots)}")
except FileNotFoundError:
    print("Erreur : Le fichier mots.txt est introuvable.")
    mots = []

# Variables du bot
bot_running = False
mode_turbo = False  # Mode Turbo désactivé par défaut
logs_enabled = True  # Activer les logs
lock = threading.Lock()

# Fonction pour trouver un mot
def trouver_mot(lettres, lettres_exclues):
    """Rechercher un mot qui contient la séquence exacte de lettres spécifiées et qui n'est pas exclu"""
    if mode_turbo:
        mots_tries = sorted(mots, key=len)  # Prioriser les mots les plus courts en mode Turbo
    else:
        mots_tries = mots

    for mot in mots_tries:
        if lettres in mot and mot[0].lower() not in lettres_exclues:
            return mot
    return None

# Fonction pour extraire les lettres à partir de l'écran avec OCR
def extraire_lettres_par_ocr(copy_x, copy_y):
    try:
        screenshot = ImageGrab.grab(bbox=(copy_x, copy_y, copy_x + 100, copy_y + 50))  # Ajuster la capture selon la zone du jeu
        texte = pytesseract.image_to_string(screenshot).strip().lower()
        log_message(f"Lettres OCR détectées : {texte}")
        return texte
    except Exception as e:
        log_message(f"Erreur OCR : {e}")
        return ""

# Fonction d'action du bot
def bot_action():
    global bot_running
    while bot_running:
        try:
            # Obtenir les coordonnées du point de copie via l'interface
            copy_x = int(copy_x_entry.get())
            copy_y = int(copy_y_entry.get())

            # Extraire les lettres via OCR
            lettres = extraire_lettres_par_ocr(copy_x, copy_y)
            if lettres == "":
                log_message("Aucune lettre détectée, réessayez.")
                continue

            lettres_exclues = exclusion_entry.get().strip().lower()
            mot = trouver_mot(lettres, lettres_exclues)

            if mot:
                log_message(f"Mot trouvé : {mot}")

                # Obtenir les coordonnées du point de saisie via l'interface
                write_x = int(write_x_entry.get())
                write_y = int(write_y_entry.get())

                pyautogui.click(x=write_x, y=write_y)

                # Conversion WPM en intervalle par caractère
                wpm = typing_speed_scale.get()
                typing_speed = 60 / (wpm * 5)

                pyautogui.write(mot, interval=typing_speed)
                pyautogui.press('enter')

                with lock:
                    if mot in mots:
                        mots.remove(mot)
            else:
                log_message("Aucun mot trouvé, attendre la prochaine série de lettres")

            reaction_speed = reaction_speed_scale.get() / 1000.0
            time.sleep(reaction_speed)
        except Exception as e:
            log_message(f"Erreur lors de l'exécution du bot : {str(e)}")
        time.sleep(0.1)  # Pause pour éviter la surcharge

# Fonction pour démarrer le bot
def start_bot_thread():
    global bot_running
    if not bot_running:
        bot_running = True
        log_message("Bot démarré.")
        threading.Thread(target=bot_action).start()

# Fonction pour arrêter le bot
def stop_bot():
    global bot_running
    bot_running = False
    log_message("Bot arrêté.")

# Fonction pour basculer le bot
def toggle_bot():
    if bot_running:
        stop_bot()
    else:
        start_bot_thread()

# Fonction pour activer/désactiver le mode Turbo
def toggle_turbo():
    global mode_turbo
    mode_turbo = not mode_turbo
    log_message(f"Mode Turbo {'activé' if mode_turbo else 'désactivé'}.")

# Fonction de gestion des logs
def log_message(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    log_text.insert(tk.END, full_message + '\n')
    log_text.see(tk.END)
    if logs_enabled:
        with open("bot_logs.txt", "a") as log_file:
            log_file.write(full_message + "\n")

# Interface utilisateur
window = tk.Tk()
window.title("Bot BombParty Amélioré")

# Bouton démarrer/arrêter
start_button = tk.Button(window, text="Démarrer/Arrêter le Bot", command=toggle_bot)
start_button.pack(pady=10)

# Bouton mode Turbo
turbo_button = tk.Button(window, text="Activer/Désactiver Mode Turbo", command=toggle_turbo)
turbo_button.pack(pady=10)

# Zone de logs
log_text = tk.Text(window, height=10, width=50)
log_text.pack(pady=10)

# Saisie des lettres à exclure
exclusion_label = tk.Label(window, text="Lettres à exclure :")
exclusion_label.pack()

exclusion_entry = tk.Entry(window)
exclusion_entry.pack()

# Coordonnées du point de copie
copy_label = tk.Label(window, text="Coordonnées du point de copie (x, y) :")
copy_label.pack()

copy_x_entry = tk.Entry(window)
copy_x_entry.pack()
copy_x_entry.insert(0, "718")

copy_y_entry = tk.Entry(window)
copy_y_entry.pack()
copy_y_entry.insert(0, "611")

# Coordonnées du point de saisie
write_label = tk.Label(window, text="Coordonnées du point de saisie (x, y) :")
write_label.pack()

write_x_entry = tk.Entry(window)
write_x_entry.pack()
write_x_entry.insert(0, "500")

write_y_entry = tk.Entry(window)
write_y_entry.pack()
write_y_entry.insert(0, "1040")

# Curseur pour ajuster la vitesse de frappe (en WPM)
typing_speed_label = tk.Label(window, text="Vitesse de frappe (en WPM) :")
typing_speed_label.pack()

typing_speed_scale = tk.Scale(window, from_=10, to=200, orient='horizontal')
typing_speed_scale.set(80)
typing_speed_scale.pack()

# Curseur pour ajuster la vitesse de réaction
reaction_speed_label = tk.Label(window, text="Vitesse de réaction (en ms) :")
reaction_speed_label.pack()

reaction_speed_scale = tk.Scale(window, from_=100, to=3000, orient='horizontal')
reaction_speed_scale.set(300)
reaction_speed_scale.pack()

# Démarrage de la vérification d'arrêt d'urgence
def check_emergency_stop_and_toggle():
    if keyboard.is_pressed('f9'):
        toggle_bot()
    window.after(500, check_emergency_stop_and_toggle)

check_emergency_stop_and_toggle()
window.mainloop()
