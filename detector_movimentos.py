#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import cv2.cv as cv
from datetime import datetime
import time


class DetectorMove():
    def mudar(self, val):  # Valor de retorno de chamada quando o usuário altera o limite de detecção
        self.limite = val

    def __init__(self, limite=25, gravar=True, showWindows=True):

        self.font = None
        self.gravar = gravar  # Registre ou não o objeto em movimento
        self.show = showWindows  # Para mostrar a janela em tempo real
        self.frame = None

        self.captura = cv.CaptureFromCAM(0)
        self.frame = cv.QueryFrame(self.captura)  # Capturando e enquadrando a imagem
        if gravar:
            self.inicioGrava()

        self.frame_cinza = cv.CreateImage(cv.GetSize(self.frame), cv.IPL_DEPTH_8U, 1)
        self.average_frame = cv.CreateImage(cv.GetSize(self.frame), cv.IPL_DEPTH_32F, 3)
        self.quadro = None
        self.quadro_anterior = None

        self.superficie = self.frame.width * self.frame.height
        self.superficie_atual = 0
        self.contornos_atuais = None
        self.limite = limite
        self.gravando = False


        if showWindows:
            cv.NamedWindow("Image")
            cv.CreateTrackbar("Limite da deteccao: ", "Image", self.limite, 100, self.mudar)

    def inicioGrava(self):  # Criando uma função para gravar o inicio dos movimentos


        self.font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 2, 8)  #Iniciando uma font

    def run(self):
        started = time.time()
        while True:

            currentframe = cv.QueryFrame(self.captura)
            tempo = time.time()  #Para obter timestamp do quadro

            self.processImage(currentframe)  # Processando a imagem

            if not self.gravando:
                if self.movendo():

                    if tempo > started + 10:  #  Para Aguardar 10 segundos após o início da webcam para ajuste de luminosidade.
                        print "Algo esta se movendo !"
                        if self.gravar:  # Gravano ou mostrando no vídeo
                            self.gravando = True
                cv.DrawContours(currentframe, self.contornos_atuais, (0, 0, 255), (0, 255, 0), 1, 2, cv.CV_FILLED)
            else:
                if tempo >= self.trigger_time + 10:  # Grava durante 10 segundos
                    print "Pare de gravar"
                    self.gravando = False


            if self.show:
                cv.ShowImage("Imagem", currentframe)

            sair = cv.WaitKey(1) % 0x100
            if sair == 27 or sair == 10:    # Será Verificado se o usuário pressionou a tecla ESC
                break

    def processImage(self, frame):
        cv.Smooth(frame, frame)  # Remove os falsos positivos

        if not self.quadro:  # Para primeira vez, coloque valores em diferença, temp e moving_average
            self.quadro = cv.CloneImage(frame)
            self.quadro_anterior = cv.CloneImage(frame)
            cv.Convert(frame, self.average_frame)  # Deve converter porque depois de corregar
        else:
            cv.RunningAvg(frame, self.average_frame, 0.05)  # Calcule a média

        cv.Convert(self.average_frame, self.quadro_anterior)  # Converter de volta para o quadro 8U

        cv.AbsDiff(frame, self.quadro_anterior, self.quadro)  # curva média móvel

        cv.CvtColor(self.quadro, self.frame_cinza, cv.CV_RGB2GRAY)  # Converte para cinza, caso contrário, não pode fazer o limite
        cv.Threshold(self.frame_cinza, self.frame_cinza, 50, 255, cv.CV_THRESH_BINARY)

        cv.Dilate(self.frame_cinza, self.frame_cinza, None, 15)  # para obter blobs de objeto
        cv.Erode(self.frame_cinza, self.frame_cinza, None, 10)

    def movendo(self):

        # Find contours
        storage = cv.CreateMemStorage(0)
        contours = cv.FindContours(self.frame_cinza, storage, cv.CV_RETR_EXTERNAL, cv.CV_CHAIN_APPROX_SIMPLE)

        self.contornos_atuais = contours  # Salva os contornos da imagem

        while contours:  # Para todos os contornos calcule a área
            self.superficie_atual += cv.ContourArea(contours)
            contours = contours.h_next()

        avg = (self.superficie_atual * 100) / self.superficie  # Calcule a média da área de contorno no tamanho total
        self.superficie_atual = 0  # Coloque de volta a superfície atual para 0

        if avg > self.limite:
            return True
        else:
            return False


if __name__ == "__main__":
    detect = DetectorMove(gravar=True)
    detect.run()