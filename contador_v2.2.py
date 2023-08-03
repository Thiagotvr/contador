import cv2
import numpy as np
import pandas as pd
from datetime import datetime

video = cv2.VideoCapture(1)
contador = 0
liberado = False

# Cria um DataFrame vazio para armazenar os dados
dados = pd.DataFrame(columns=["Data e Hora", "Contador"])

while True:
    ret, img = video.read()
    img = cv2.resize(img, (1100, 720))
    imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    x, y, w, h = 208, 142, 46, 332
    imgTh = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 12)
    kernel = np.ones((8, 8), np.uint8)
    imgDil = cv2.dilate(imgTh, kernel, iterations=2)

    recorte = imgDil[y:y + h, x:x + w]
    brancos = cv2.countNonZero(recorte)
    #print(brancos)

    if brancos > 2500 and liberado == True:
        contador += 1
    if brancos < 2500:
        liberado = True
    else:
        liberado = False

    if liberado == False:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 4)
    else:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 4)

    cv2.rectangle(imgTh, (x, y), (x + w, y + h), (255, 255, 255), 6)

    cv2.putText(img, str(brancos), (x - 30, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1)

    # Verifica se passou 1 minuto para salvar os dados no DataFrame e na planilha
    if datetime.now().second == 0:
        print("Quantidade de garrafas que passaram: ", contador)
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dados = pd.concat([dados, pd.DataFrame({"Data e Hora": [data_hora], "Contador": [contador]})],
                          ignore_index=True)

        # Calcula a média do contador por minuto
        media_por_minuto = dados["Contador"].mean()
        cv2.putText(img, f"Média/min: {media_por_minuto:.2f}", (x + 100, y + 60), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 0, 0), 2)

    # Obtém apenas o horário em tempo real e exibe na imagem
    horario_atual = datetime.now().strftime("%H:%M:%S")
    cv2.putText(img, f"Horario: {horario_atual}", (x + 100, y + 120), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 255), 2)

    caminho = "D:\Conecthus\Projetos\EspCam\dados_contador.csv"
    dados.to_csv(caminho, index=False, sep=";")

    cv2.putText(img, str(contador), (x + 100, y), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 0), 5)

    cv2.imshow('video original', img)
    cv2.imshow('video', cv2.resize(imgTh, (600, 500)))

    key = cv2.waitKey(20)
    if key == 27:
        break

video.release()
cv2.destroyAllWindows()
