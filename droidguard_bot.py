#!/data/data/com.termux/files/usr/bin/python
import os, sys, time, json, base64, subprocess, requests, hashlib

FIREBASE_URL = "https://droidguard-10597-default-rtdb.firebaseio.com/"

print("🟢 DroidGuard Bot Iniciado!")
device_id = hashlib.md5(os.uname().nodename.encode()).hexdigest()[:8]
print(f"📱 Device ID: {device_id}")

# Teste básico
print("✅ Bot está rodando!")

# Loop simples
while True:
    try:
        # Só para manter vivo
        print("💓 Heartbeat")
        time.sleep(30)
    except KeyboardInterrupt:
        print("🛑 Bot finalizado")
        break
