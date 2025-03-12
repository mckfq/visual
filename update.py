from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import json

# 🖥 URL de la page
url_page = "https://www.stream4free.tv/m6-live-streaming"

# 📄 Fichier M3U à modifier
fichier_m3u = "geral.m3u"

# ✅ Activer l'interception réseau avec DevTools Protocol
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# 🌐 Lancer Chrome avec interception réseau
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 🔽 Charger la page
    driver.get(url_page)
    time.sleep(10)  # Laisser le temps au JS de charger

    # 🔎 Récupérer les logs réseau
    logs = driver.get_log("performance")
    
    urls_m3u8 = []
    
    # 🕵️‍♂️ Rechercher toutes les URLs M3U8 dans les requêtes réseau
    for log in logs:
        message = json.loads(log["message"])  # Convertir le log en JSON
        if "params" in message and "request" in message["params"]:
            request = message["params"]["request"]
            if ".m3u8" in request.get("url", ""):
                urls_m3u8.append(request["url"])

    if urls_m3u8:
        print(f"✅ {len(urls_m3u8)} URL(s) M3U8 trouvée(s) via le réseau :")
        for url in urls_m3u8:
            print(f"🔗 {url}")

        # ✅ Prendre la première URL trouvée
        nouvelle_url = urls_m3u8[0]

        # 🔄 Mettre à jour uniquement la ligne de l'URL M3U8
        with open(fichier_m3u, "r") as file:
            lines = file.readlines()

        with open(fichier_m3u, "w") as file:
            update_next_line = False
            for line in lines:
                if update_next_line and line.startswith("http"):
                    print(f"🔄 Mise à jour de l'URL : {line.strip()} → {nouvelle_url}")
                    file.write(nouvelle_url + "\n")  # Remplace uniquement l'URL
                    update_next_line = False
                else:
                    file.write(line)
                    if 'tvg-id="M6.fr"' in line:  
                        update_next_line = True  

        print(f"✅ M6 mis à jour avec la nouvelle URL dans {fichier_m3u} !")

    else:
        print("⚠️ Aucune URL M3U8 détectée dans le réseau.")

finally:
    driver.quit()  # Fermer Selenium proprement
