#!/data/data/com.termux/files/usr/bin/bash
# DroidGuard - Inicializador (baixa e executa o bot do GitHub)

echo "🔄 Baixando DroidGuard do GitHub..."

# Baixar o bot mais recente
curl -s -o /tmp/droidguard_bot.py https://raw.githubusercontent.com/gynbetfc/liveandroid/main/droidguard_bot.py

# Dar permissão
chmod +x /tmp/droidguard_bot.py

# Executar
echo "🚀 Iniciando DroidGuard..."
python /tmp/droidguard_bot.py

# Se chegar aqui, o bot morreu
echo "❌ Bot finalizado"
