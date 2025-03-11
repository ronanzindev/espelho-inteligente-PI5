import time
import json
import queue
import sys
import os
import speech_recognition as sr
from vosk import Model, KaldiRecognizer

# Caminho para o modelo de reconhecimento de voz (ajuste se necessário)
MODEL_PATH = "vosk-model-small-pt-0.3"  

# Inicializar o modelo VOSK
if not os.path.exists(MODEL_PATH):
    print("ERRO: O modelo VOSK não foi encontrado! Baixe de https://alphacephei.com/vosk/models e extraia para o diretório do projeto.")
    sys.exit(1)

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

def listen_for_keyword(keyword="espelho mágico"):
    """ Aguarda o usuário dizer a palavra-chave antes de ativar o sistema. """
    print(f"Aguardando a palavra-chave '{keyword}'...")

    mic = sr.Microphone()
    with mic as source:
        recognizer_vosk = sr.Recognizer()
        recognizer_vosk.adjust_for_ambient_noise(source)  # Ajuste para reduzir ruído

        while True:
            print("Ouvindo...")
            try:
                audio = recognizer_vosk.listen(source)
                audio_data = audio.get_raw_data(convert_rate=16000, convert_width=2)  # Converte para 16kHz
                
                if recognizer.AcceptWaveform(audio_data):  
                    result = json.loads(recognizer.Result())  
                    texto = result.get("text", "").lower()

                    print(f"Você disse: {texto}")

                    if keyword in texto:
                        print("Palavra-chave detectada! Iniciando reconhecimento...")
                        return  # Sai da função para ativar o reconhecimento facial
                
            except Exception as e:
                print(f"Erro no reconhecimento: {e}")
