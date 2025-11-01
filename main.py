#!/usr/bin/env python3
"""
Détecteur d'applications pour Home Assistant
Version ultra-légère - Compilable en exe
"""

import time
import json
import urllib.request
import ctypes
import ctypes.wintypes
import os
from datetime import datetime

# Configuration Home Assistant
WEBHOOK_URL = "http://homeassistant.local:8123/api/webhook/jeux"
CHECK_INTERVAL = 10  # Secondes
SEND_ONLY_CHANGES = True

# Liste des jeux
GAME_KEYWORDS = [
    'game', 'steam', 'epic', 'minecraft', 'league', 'valorant',
    'fortnite', 'apex', 'overwatch', 'discord', 'battle.net',
    'origin', 'uplay', 'genshin', 'riot', 'blizzard', 'wow',
    'call of duty', 'cod', 'battlefield', 'fifa', 'nba',
    'assassin', 'creed', 'far cry', 'rainbow', 'pubg',
    'counter-strike', 'csgo', 'cs2', 'dota', 'hearthstone',
    'diablo', 'starcraft', 'warcraft', 'roblox', 'among us'
]

class HomeAssistantDetector:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.last_app = None
        self.last_title = None
        
    def get_active_window(self):
        """Récupère la fenêtre active"""
        try:
            hwnd = self.user32.GetForegroundWindow()
            if not hwnd:
                return None, None
                
            # Titre de la fenêtre
            length = 256
            buff = ctypes.create_unicode_buffer(length)
            self.user32.GetWindowTextW(hwnd, buff, length)
            window_title = buff.value
            
            if not window_title:
                return None, None
                
            # Process ID
            pid = ctypes.wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # Nom du processus
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            process_handle = self.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            
            if process_handle:
                exe_name = ctypes.create_unicode_buffer(260)
                size = ctypes.wintypes.DWORD(260)
                
                if self.kernel32.QueryFullProcessImageNameW(
                    process_handle, 0, exe_name, ctypes.byref(size)
                ):
                    self.kernel32.CloseHandle(process_handle)
                    process_path = exe_name.value
                    process_name = os.path.basename(process_path)
                    return process_name, window_title
                    
                self.kernel32.CloseHandle(process_handle)
                
        except Exception:
            pass
            
        return None, None
    
    def is_game(self, process_name, window_title):
        """Détecte si c'est un jeu"""
        if not process_name:
            return False
            
        check_string = f"{process_name} {window_title or ''}".lower()
        return any(keyword in check_string for keyword in GAME_KEYWORDS)
    
    def send_to_home_assistant(self, process_name, window_title, is_game):
        """Envoie à Home Assistant"""
        try:
            # Format pour Home Assistant
            data = {
                "state": "gaming" if is_game else "working",
                "attributes": {
                    "process_name": process_name,
                    "window_title": window_title,
                    "is_game": is_game,
                    "category": "game" if is_game else "application",
                    "user": os.environ.get('USERNAME', 'Unknown'),
                    "computer": os.environ.get('COMPUTERNAME', 'Unknown'),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=3) as response:
                return response.status == 200
        except:
            return False
    
    def test_connection(self):
        """Test la connexion à Home Assistant"""
        print("🔍 Test de connexion à Home Assistant...")
        
        test_data = {
            "state": "testing",
            "attributes": {
                "message": "Test de connexion",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            json_data = json.dumps(test_data).encode('utf-8')
            req = urllib.request.Request(
                WEBHOOK_URL,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    print("✅ Connexion réussie!\n")
                    return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            print(f"   URL: {WEBHOOK_URL}\n")
            
        return False
    
    def run(self):
        """Boucle principale"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("╔════════════════════════════════════════╗")
        print("║   🎮 DETECTEUR POUR HOME ASSISTANT    ║")
        print("╚════════════════════════════════════════╝")
        print(f"\n📡 Webhook: {WEBHOOK_URL}")
        print(f"⏱️  Intervalle: {CHECK_INTERVAL}s\n")
        
        if not self.test_connection():
            input("Appuyez sur Entrée pour continuer quand même...")
        
        print("👀 Surveillance active... (Ctrl+C pour arrêter)\n")
        print("─" * 45)
        
        error_shown = False
        
        while True:
            try:
                process_name, window_title = self.get_active_window()
                
                if process_name:
                    # Vérifier les changements
                    if SEND_ONLY_CHANGES:
                        if process_name == self.last_app and window_title == self.last_title:
                            time.sleep(CHECK_INTERVAL)
                            continue
                    
                    # Détecter le type
                    is_game = self.is_game(process_name, window_title)
                    
                    # Envoyer à HA
                    if self.send_to_home_assistant(process_name, window_title, is_game):
                        current_time = datetime.now().strftime("%H:%M:%S")
                        icon = '🎮' if is_game else '💻'
                        status = '[JEU]' if is_game else '[APP]'
                        
                        display_name = process_name[:25] + "..." if len(process_name) > 25 else process_name
                        print(f"[{current_time}] {icon} {display_name:<28} {status}")
                        
                        self.last_app = process_name
                        self.last_title = window_title
                        error_shown = False
                    elif not error_shown:
                        print("⚠️  Erreur de connexion à Home Assistant")
                        error_shown = True
                
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Arrêt du détecteur...")
                
                # Notifier Home Assistant
                try:
                    shutdown_data = {
                        "state": "idle",
                        "attributes": {
                            "message": "Détecteur arrêté",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                    
                    json_data = json.dumps(shutdown_data).encode('utf-8')
                    req = urllib.request.Request(
                        WEBHOOK_URL,
                        data=json_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    urllib.request.urlopen(req, timeout=2)
                    print("✅ Home Assistant notifié")
                except:
                    pass
                
                break
            except:
                time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if os.name != 'nt':
        print("❌ Ce programme ne fonctionne que sur Windows!")
        exit(1)
    
    detector = HomeAssistantDetector()
    detector.run()