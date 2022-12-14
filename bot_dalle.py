import json
import requests
from time import time, sleep
import os
import openai
import telepot
import logging
import my_api
token = my_api.easyig_bot_API_KEY
openaiApiKey = my_api.OpenAi_API_KEY

logging.basicConfig(filename='bot.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def downloadImage(url, prompt, chat_id, from_name, from_username):
    """Scarica e salva su disco l'immagine creata da AI"""
    nome_file = str(int(time()))
    # salvo nella cartella immagini
    f = open(f'immagini/{nome_file}.png', 'wb')
    response = requests.get(url)
    f.write(response.content)
    f.close()
    f = open(f'immagini/{nome_file}.txt', 'w')
    f.write('Username:'+from_username+' Name:'+from_name +
            ' Chat_Id:'+str(chat_id)+' Testo Richiesta:'+prompt)
    f.close()
    # salvo immagine per successivo invio in chat
    f = open('photo.png', 'wb')
    f.write(response.content)
    f.close()
    f = open('photo.txt', 'w')
    f.write(prompt)
    f.close()
    logging.info(
        f'{from_username} - {from_name} - {chat_id} - {prompt} - download successful')
    #print("download successful")
    return True


def saveUsers(from_username):
    # creo una lista di utenti che hanno utilizzato il servizio
    f = open("users.log", "a")
    f.write(f"@{from_username},")
    f.close()


def saveSingleUsers():
    f = open("users.log", "r")
    users = f.read()
    f.close()
    dirtyUsersList = users.split(sep=",")
    usersDict = {}
    for el in dirtyUsersList:
        if el in usersDict:
            usersDict[el] += 1
        else:
            usersDict[el] = 0
    f = open("singleUsers.log", "w")
    json.dump(usersDict, f)
    f.close()
    stringa = json.dumps(usersDict)
    return stringa


def readLog(param=1):
    f = open("bot.log", "r")
    log = f.read()
    f.close()
    if param == 1:
        log = log[-1500:]
    return log


def getNewImage(prompt, chat_id, from_name, from_username, n=1, size="512x512"):
    """crea la connessione con Dall-e, 
    richiede una nuova immagine descritta nel prompt, 
    della grandess definita in size, e 
    chiama la funzione scaricaImmagine() per salvarla sul disco"""
    openai.api_key = openaiApiKey
    response = openai.Image.create(
        #prompt="A bicycle running to the moon and a baby in bicycle basket",
        prompt=prompt,
        n=n,
        # size="1024x1024"
        size=size
    )
    logging.info(
        f'{from_username} - {from_name} - {chat_id} - {prompt} - OpenAi response received')
    stringa = json.dumps(response)
    dizionario = json.loads(stringa)
    for el in dizionario['data']:
        image_url = el['url']
        imgReceived = downloadImage(
            image_url, prompt, chat_id, from_name, from_username)
    return True


def handle(msg):
    try:
        content_type, chat_type, chat_id = telepot.glance(msg)
        from_name = msg['from']['first_name']
        from_username = msg['from']['username']
        saveUsers(from_username)

        if content_type == 'text':
            msg_received = msg['text']

            if "/start" in msg_received:
                bot.sendMessage(
                    chat_id, f"Grazie aver iniziato questa chat {from_name}, \nTi ricordo che per ottenere la tua immagine\ndevi iniziare il messaggio con #getimage e descrivere al meglio ciò che vuoi ottenere\n\nSe non riterrò valida la descrizione dovrai modificarla ")
                logging.info(
                    f'{from_username} - {from_name} - {chat_id} - Ricevuta richiesta /start')
                return
            if "/users" in msg_received:
                testo = saveSingleUsers()
                bot.sendMessage(chat_id, testo)
                logging.info(
                    f'{from_username} - {from_name} - {chat_id} - Ricevuta richiesta /users')
                return
            if "/log" in msg_received:
                param = msg_received[4:]
                if param.isnumeric():
                    stringa = readLog(param)
                else:
                    stringa = readLog(param=1)
                bot.sendMessage(
                    chat_id, stringa)
                logging.info(
                    f'{from_username} - {from_name} - {chat_id} - Ricevuta richiesta /log')
                return

            if "#getimage" in msg_received:
                prompt = msg_received[9:]
                if len(prompt) > 40:
                    bot.sendMessage(
                        chat_id, "Ho ricevuto il tuo testo\nAdesso controllo se è valido.....")
                    sleep(5)
                    bot.sendMessage(
                        chat_id, f"OK! {from_name} - : adesso Creo una immagine con queste caratteristiche \n" + prompt + "Ci vorrà qualche decina di secondi.....\nAspetta!")
                    if getNewImage(prompt, chat_id, from_name, from_username):
                        photo = open('photo.png', 'rb')
                        bot.sendPhoto(chat_id, photo=photo)
                        photo.close()
                        logging.info(
                            f"{from_username} - {from_name} - {chat_id} - {prompt} - Processo di creazione dell'immagine andato a buon fine")
                    else:
                        bot.sendMessage(
                            chat_id, f"{from_name} - Si è verificato un problema,\nnon ho l'immagine.\nPerdono!")
                        logging.info(
                            f"{from_username} - {from_name} - {chat_id} - {prompt} - Processo di creazione dell'immagine Fallito")
                else:
                    bot.sendMessage(
                        chat_id, "La descrizione dell'immagine non è sufficiente,\ndefinisci meglio cosa vuoi ottenere,\nmeglio descrivi la tua immagine e più carina verrà\nricordati di scrivere in inglese")
                    logging.info(
                        f"{from_username} - {from_name} - {chat_id} - {msg_received} - Uncorrect requests - nessun risultato inviato")

            else:
                bot.sendMessage(
                    chat_id, f"{from_name} - Non ho riconosciuto la tua richiesta\n\nTi ricordo che la richiesta deve essere preceduta da #getimage\ne deve essere il più possibile dettagliata\nper ottenere una immagine migliore")
                logging.info(
                    f"{from_username} - {from_name} - {chat_id} - {msg_received} - Richiesta non Riconosciuta - nessun risultato inviato")
    except Exception as e:
        logging.warning("*****ECCEZIONE NELLA FUNZIONE handle():   ")
        logging.warning(e)
        bot.sendMessage(chat_id, "Operazione Fallita - eccezione ricevuta")


# faccio partire il Bot e aspetto messaggi in arrivo
# @easyig_bot API_KEY Token
TOKEN = token
bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
logging.info("Start Listening on Telegram ..")
#print('Listening ...')
# tengo vivo il programma semplicemente aspettando
while 1:
    sleep(10)
