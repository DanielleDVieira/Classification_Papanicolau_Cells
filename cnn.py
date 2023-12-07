from matplotlib.pyplot import imread
from matplotlib.pyplot import imshow
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.imagenet_utils import decode_predictions
from tensorflow.keras.applications.imagenet_utils import preprocess_input
import cv2
import numpy as np
import tensorflow as tf
import os.path
from os import listdir
from os.path import isfile, join
import pandas as pd
from sklearn import metrics as me
import matplotlib.pyplot as plt
from collections import Counter

def binary_cnn_cell_classifier(filename):
    # Pegando classificacao correta de cada celula da imagem escolhida
    df = pd.read_csv("./data/classifications.csv")
    features = df[df['image_filename'] == filename]
    y_test = features[['bethesda_system']]

    # Lendo cada célula da imagem e calculando a probabilidade para cada classe para classificacao
    predsAll = []
    cells_id = []
    classifications = []
    filename_without_png = filename.split(".")[0]
    onlyfiles = [f for f in listdir(f"./recorteImg/{filename_without_png}") if isfile(join(f"./recorteImg/{filename_without_png}", f))]
    print(onlyfiles)
    for img in onlyfiles:
        cells_id.append(img.split(".")[0])
        img = cv2.imread(f"./recorteImg/{filename_without_png}/{img}")
        img = cv2.resize(img, (224, 224))

        x = np.expand_dims(img, axis=0)
        x = preprocess_input(x)

        binary_cnn = tf.keras.models.load_model('./data/binary_cnn')
        preds = binary_cnn.predict(x)
        print(preds)
        predsAll.append(preds)     
        
    # Classificando as células com base na maior probabilidade
    for i in range(len(predsAll)):
        predSplit = np.array_split(predsAll[i][0], 2)
        if (predSplit[0] > predSplit[1]):
            classifications.append(0)
        else:
            classifications.append(1)

    print(Counter(classifications))

    # Acrescentar no dataframe que contem os descritores da imagem a coluna com sua classificacao
    classificationCSV = pd.DataFrame({'ID': cells_id})
    classificationCSV['Classification'] = classifications
    # Acrescentar no dataframe que contem os descritores da imagem a coluna com a classificacao correta
    classificationCSV['Correct_Classification'] = y_test['bethesda_system'].values
    # Substituir os valores na coluna 'Classe'
    mapeamento = {0: 'Negative', 1: 'Positive'}
    classificationCSV['Classification'] = classificationCSV['Classification'].replace(mapeamento)
    print(classificationCSV)
    # Gravar novo arquivo csv com a classificacao binaria das células
    classificationCSV.to_csv(f'./data/classificationCell/binary_CNN_{filename_without_png}.csv', index=False)

    y_test.replace({
        'Negative for intraepithelial lesion': 0,
        'HSIL': 1,
        'LSIL': 1,
        'ASC-H': 1,
        'ASC-US': 1,
        'SCC': 1
    }, inplace=True)
    print(f"{y_test.value_counts()}")

    acuracia = me.accuracy_score(y_test, classifications) * 100
    print("Acurácia:", acuracia)

    precisao = me.precision_score(y_test, classifications, zero_division=0) * 100
    print("Precisão:", precisao)

    sensibilidade = me.recall_score(y_test, classifications, zero_division=0) * 100
    print("Sensibilidade (Revocação):", sensibilidade)

    cm = me.confusion_matrix(y_test, classifications)
    #classes = ['Negative', 'Positive']  # Mapeamento para 0 e 1
    # Plotando a matriz de confusão
    fig, ax = plt.subplots(figsize=(8, 8))
    disp = me.ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(include_values=True, cmap='Blues', ax=ax, xticks_rotation='horizontal')
    # Adicionando título
    plt.title('Matriz de confusão para classificação binária com CNN', pad=60, weight='bold', ha='center')
    plt.text(0.5, -0.15, f'Acurácia: {acuracia:.2f}%', ha='center', fontsize=10, transform=ax.transAxes, weight='bold')
    plt.text(0.5, -0.2, f'Precisão: {precisao:.2f}%', ha='center', fontsize=10, transform=ax.transAxes, weight='bold')
    plt.text(0.5, -0.25, f'Sensibilidade: {sensibilidade:.2f}%', ha='center', fontsize=10, transform=ax.transAxes, weight='bold')
    plt.savefig(f"./matrizConfusao/binary_Cell_CNN_{filename}")
    # Exibindo a matriz de confusão
    plt.show()

    print(predsAll)

def multiclass_cnn_cell_classifier(filename):
    print("oi")