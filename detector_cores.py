#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Este código só detecta a cor azul"""
import cv2
import numpy as np

#Capture o quadro de entrada da webcam
def detecta_Cor(cap, fator_escala):
    # Capitura o objeto que ira aparecer no video
    ret, frame = cap.read()

    # Aqui redimensiona o quadro de entrada
    frame = cv2.resize(frame, None, fx=fator_escala,
            fy=fator_escala, interpolation=cv2.INTER_AREA)

    return frame

if __name__=='__main__':
    cap = cv2.VideoCapture(0)
    fator_escala = 0.5

    # A janela ficará aberta até que o usuário pressione a tecla ESC
    while True:
        frame = detecta_Cor(cap, fator_escala)

        # Converção o espaço de cores do HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Definir intervalo 'azul' no espaço de cores HSV
        baixo = np.array([60,100,100])
        alto = np.array([180,255,255])

        # Limite a imagem do HSV para obter apenas a cor azul
        mascara = cv2.inRange(hsv, baixo, alto)

        # Aplicando máscara e imagem original
        saida = cv2.bitwise_and(frame, frame, mask=mascara)
        saida = cv2.medianBlur(saida, 5)

        cv2.imshow('Imagem original', frame)
        cv2.imshow(' Detector de cores', saida)

        # Será Verificado se o usuário pressionou a tecla ESC
        fecharJanela = cv2.waitKey(5)
        if fecharJanela  == 27:
            break

    cv2.destroyAllWindows()