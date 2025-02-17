import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import requests
from urllib.parse import urlparse, parse_qs

# Configurações do .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")
DISCORD_URL = os.getenv("DISCORD_URL")

# logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def escape_markdown(text):
    return text.replace('.', '\\.')

# Funções
def consultar_dados(id):
    url = f"{API_URL}?uid={id}" 
    logger.info(f"Consultando dados para o ID: {id}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança uma exceção se o código HTTP não for 2xx
        dados = response.json()

        logger.info(f"Resposta da API: {dados}")

        # Verifica se o status é 'success'
        if dados.get("status") == "success":
            is_banned = dados.get("is_banned", 0)  # 1 para banido, 0 para não banido
            period = dados.get("period", 0)
            message = dados.get("message", "Mensagem não especificada.")
            credits = dados.get("credits", "https://t.me/ngxjs")  # Link de créditos
            uid = dados.get("uid", id)

            # Mensagem de retorno com base no status de banimento
            if is_banned == 1:
                return (
                    f"🔒 *ID:* {uid}\n"
                    f"🚫 *Banido:* Sim\n"
                    f"🧑‍💻 *Ban Code:* `{period}`\n"
                    f"\n"
                    f"{message}\n\n"  # Exibe a mensagem de banimento da API
                    f"🤖 [Bot Criado Por](https://t.me/ngxjs)\n"
                    f"🔗 [Api Feito Por](https://upload.spgunk.eu.org)\n"
                    f"💬 Créditos: [@ngxjs]({credits})"
                )
            else:
                return (
                    f"🔒 *ID:* {uid}\n"
                    f"🚫 *Banido:* Não\n\n"
                    f"{message}\n\n"
                    f"🤖 [Bot Criado Por](https://t.me/ngxjs)\n"
                    f"🔗 [Api Feito Por](https://upload.spgunk.eu.org)\n"
                    f"💬 Créditos: [@ngxjs]({credits})"
                )
        else:
            # Caso o status não seja 'success', retorna a mensagem de erro da API
            logger.error(f"Erro na API: {dados.get('message', 'Mensagem não especificada.')}") 
            return f"Erro da API: {dados.get('message', 'Mensagem não especificada.')}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao acessar a API. Detalhes: {e}")
        return f"Erro ao acessar a API. Detalhes: {e}"

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Olá! Bem-vindo ao bot checker de banimentos!")
    await update.message.reply_text("Envie o ID que você deseja consultar.")

async def consultar_id(update: Update, context: CallbackContext) -> None:
    id = update.message.text.strip()  # Garantir que não haja espaços extras

    # Verificar se o texto enviado contém uma URL com o parâmetro "uid"
    if "http" in id:
        parsed_url = urlparse(id)
        query_params = parse_qs(parsed_url.query)
        if "uid" in query_params:
            id = query_params["uid"][0]  # Obtendo o valor de "uid" da URL
        else:
            await update.message.reply_text("A URL não contém o parâmetro 'uid'. Por favor, envie um ID válido.")
            return

    # Verificando se o ID é válido
    if not id.isdigit() or len(id) < 5 or len(id) > 15:
        await update.message.reply_text("Por favor, insira um ID válido (somente números com 5 a 15 dígitos).")
        return

    logger.info(f"Consultando dados para o ID: {id}")  # Log de verificação do ID

    resposta = consultar_dados(id) 
    resposta = escape_markdown(resposta)
    await update.message.reply_text(resposta, parse_mode='MarkdownV2')

    keyboard = [[InlineKeyboardButton("Entrar no meu servidor do Discord", url=DISCORD_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Entre no meu servidor do Discord:", reply_markup=reply_markup)

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Envie um ID para consulta. Use /start para reiniciar a conversa.")

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, consultar_id))
    application.add_handler(CommandHandler("help", help_command))

    logger.info("Bot está rodando...")
    application.run_polling()

if __name__ == "__main__":
    main()
