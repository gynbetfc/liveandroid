#!/data/data/com.termux/files/usr/bin/bash
echo "🔄 Baixando DroidGuard..."
curl -s -o /tmp/droidguard_bot.py https://raw.githubusercontent.com/gynbetfc/liveandroid/main/droidguard_bot.py
chmod +x /tmp/droidguard_bot.py
echo "🚀 Iniciando..."
python /tmp/droidguard_bot.py
echo "❌ Bot finalizado"
