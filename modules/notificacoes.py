import pygame
import datetime
import csv
import os

def tocar_alerta(caminho_som):
    pygame.mixer.init()
    pygame.mixer.music.load(caminho_som)
    pygame.mixer.music.play()

def log_evento(evento, valor=None, arquivo="logs/eventos.csv"):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open(arquivo, "a", newline="") as f:
        writer = csv.writer(f)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, evento, valor])
