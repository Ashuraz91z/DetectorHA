# 🎮 Détecteur d'Applications pour Home Assistant

Détecte automatiquement les jeux et applications actives sur Windows et envoie l'info à Home Assistant.

## 📥 Télécharger le .exe

**Pas besoin de Python !** Télécharge directement l'exécutable :

1. Va dans l'onglet **[Actions](../../actions)** de ce repo
2. Clique sur le dernier build réussi (✅ vert)
3. Télécharge `HomeAssistant-Detector-Windows` en bas de la page
4. Extrais le .zip et lance `HomeAssistant-Detector.exe`

## ⚙️ Configuration

Avant de lancer, modifie l'URL dans `main.py` (ligne 15) :

```python
WEBHOOK_URL = "http://TON-HOME-ASSISTANT:8123/api/webhook/jeux"
```

Remplace par l'adresse de ton Home Assistant.

## 🚀 Utilisation

### Méthode 1 : Avec le .exe (recommandé)
1. Télécharge le .exe depuis les Actions
2. Double-clique dessus
3. Le programme tourne en arrière-plan

### Méthode 2 : Avec Python
```bash
python main.py
```

## 🏠 Configuration Home Assistant

Ajoute ce webhook dans `configuration.yaml` :

```yaml
automation:
  - alias: "Détection de jeu"
    trigger:
      - platform: webhook
        webhook_id: jeux
    action:
      - service: notify.notify
        data:
          message: "{{ trigger.data.attributes.process_name }}"
```

## 🎯 Fonctionnalités

- ✅ Détecte les jeux automatiquement
- ✅ Envoie à Home Assistant en temps réel
- ✅ Ultra léger (pas de dépendances)
- ✅ Fonctionne en arrière-plan
- ✅ Compatible Windows 10/11

## 📝 Lancer au démarrage de Windows

1. Appuie sur `Win + R`
2. Tape `shell:startup`
3. Copie le raccourci du .exe dans ce dossier

## 🛠️ Développement

Pour compiler toi-même :

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
```

Le .exe sera dans le dossier `dist/`
