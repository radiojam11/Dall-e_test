import json
import requests
from time import time, sleep
import os
import openai
import telepot
import my_api.easyig_bot_API_KEY as token
import my_api.OpenAi_API_KEY as openaiApiKey


def downloadImage(url, prompt):
    """Scarica e salva su disco l'immagine creata da AI"""
    nome_file = str(int(time()))
    # salvo nella cartella immagini
    f = open(f'immagini/{nome_file}.png', 'wb')
    response = requests.get(url)
    f.write(response.content)
    f.close()
    f = open(f'immagini/{nome_file}.txt', 'w')
    f.write(prompt)
    f.close()
    # salvo immagine per successivo invio in chat
    f = open('photo.png', 'wb')
    f.write(response.content)
    f.close()
    f = open('photo.txt', 'w')
    f.write(prompt)
    f.close()

    print("download successful")
    return True


def getNewImage(prompt, n=1, size="512x512"):
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
    stringa = json.dumps(response)
    dizionario = json.loads(stringa)
    for el in dizionario['data']:
        image_url = el['url']
        imgReceived = downloadImage(image_url, prompt)
    return True


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        msg_received = msg['text']
        from_name = msg['from']['first_name']
        from_username = msg['from']['username']
        bot.sendMessage(
            chat_id, f"Grazie per il tuo messaggio {from_name}, \nElaboro...")
        if "#vogliounaimmagine" in msg_received:
            bot.sendMessage(
                chat_id, "Ho ricevuto il tuo testo\nAdesso controllo se è valido.....")
            prompt = msg_received[18:]
            bot.sendMessage(
                chat_id, "Sto Creando una immagine con queste caratteristiche \n" + prompt)
            bot.sendMessage(
                chat_id, "Ci vuole qualche decina di secondi..... Aspetta!")
            if getNewImage(prompt):
                photo = open('photo.png', 'rb')
                bot.sendPhoto(chat_id, photo=photo)
                photo.close()
            else:
                bot.sendMessage(
                    chat_id, "Si è verificato un problema,\nnon ho l'immagine.\nPerdono!")
        else:
            bot.sendMessage(
                chat_id, "Non hai richiesto una nuova immagine, \noppure la richiesta non è andata a buon fine.\nCiao")


# faccio partire il Bot e aspetto messaggi in arrivo
# @easyig_bot API_KEY Token
TOKEN = token
bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print('Listening ...')
# tengo vivo il programma semplicemente aspettando
while 1:
    sleep(10)
