import pandas as pd
import matplotlib.pyplot as plt
import math
import cv2
import os
from collections import Counter
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.spatial.distance import mahalanobis
from sklearn import metrics as me

# Função para calcular a distância de Mahalanobis para a classe negativa
def mahalanobis_dist_neg(sample, mean_neg, cov_neg):
    return mahalanobis(sample, mean_neg, cov_neg)

# Função para calcular a distância de Mahalanobis para a classe positiva
def mahalanobis_dist_positive(sample, mean_positive, cov_positive):
    return mahalanobis(sample, mean_positive, cov_positive)

# Função que classifica as células da imagem com a distância de Mahalanobis
def MahalanobisBinaryClassifier(filename):
    """# Open DF"""
    df = pd.read_csv("./data/classifications.csv")
    metrics = pd.read_csv("./data/metricsAll.csv", sep=';')

    metrics.sort_values(by=['ID'], inplace=True)
    metrics = metrics.reset_index()
    del metrics['index']

    df['MedoideCalculado'] = metrics['MedoideCalculado']
    df['CoordCSV'] = metrics['CoordCSV']
    df['DistanciaDoCentro'] = metrics['DistanciaDoCentro']
    df['Area'] = metrics['Area']
    df['Perimetro'] = metrics['Perimetro']
    df['Compacidade'] = metrics['Compacidade']
    df['Excentricidade'] = metrics['Excentricidade']

    # As células que serão classificadas e testadas serão as células da imagem escolhida na interface
    features = df[df['image_filename'] == filename]    

    """# Scatter Plot"""

    df['bethesda_system'].unique()

    scc = df[df['bethesda_system'] == 'SCC']
    neg = df[df['bethesda_system'] == 'Negative for intraepithelial lesion']
    lsi = df[df['bethesda_system'] == 'LSIL']
    hsi = df[df['bethesda_system'] == 'HSIL']
    ash = df[df['bethesda_system'] == 'ASC-H']
    asu = df[df['bethesda_system'] == 'ASC-US']

    Counter(list(df['bethesda_system']))

    """# Train test split"""

    sccFeatures = scc[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    negFeatures = neg[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    lsiFeatures = lsi[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    hsiFeatures = hsi[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    ashFeatures = ash[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    asuFeatures = asu[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]

    features_test_id = features[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    features_test = features_test_id.iloc[:, 1:5].to_numpy()
    print(features_test_id)
    print(features_test)
    y_test = features[['bethesda_system']]

    X_train0, X_test0, y_train0, y_test0 = train_test_split(sccFeatures, scc['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train1, X_test1, y_train1, y_test1 = train_test_split(negFeatures, neg['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train2, X_test2, y_train2, y_test2 = train_test_split(lsiFeatures, lsi['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train3, X_test3, y_train3, y_test3 = train_test_split(hsiFeatures, hsi['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train4, X_test4, y_train4, y_test4 = train_test_split(ashFeatures, ash['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train5, X_test5, y_train5, y_test5 = train_test_split(asuFeatures, asu['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)

    X_train_neg = X_train1
    y_train_neg = y_train1

    X_train_positive = pd.concat([X_train0, X_train2, X_train3, X_train4, X_train5], ignore_index=True)
    y_train_positive = pd.concat([y_train0, y_train2, y_train3, y_train4, y_train5], ignore_index=True)

    features_train_neg = X_train_neg.iloc[:, 1:5]
    features_train_positive = X_train_positive.iloc[:, 1:5]

    # Calcular a matriz de covariância para a classe negativa
    cov_neg = np.cov(features_train_neg, rowvar=False)
    mean_neg = np.mean(features_train_neg, axis=0)

    cov_positive = np.cov(features_train_positive, rowvar=False)
    mean_positive = np.mean(features_train_positive, axis=0)
   
    # Calcular a distância de Mahalanobis para cada amostra de teste
    distances_neg = [mahalanobis_dist_neg(sample, mean_neg, cov_neg) for sample in features_test]
    distances_positive = [mahalanobis_dist_positive(sample, mean_positive, cov_positive) for sample in features_test]

    df['Classification'] = -1
    classification = []

    for i in range(len(distances_neg)):
        if distances_neg[i] > distances_positive[i]:
            id = features_test_id.iloc[i]['cell_id']
            df.loc[df['cell_id'] == id, 'Classification'] = 1
            classification.append(1)
        else:
            id = features_test_id.iloc[i]['cell_id']
            df.loc[df['cell_id'] == id, 'Classification'] = 0       
            classification.append(0)

    print(len(features_test_id))
    print(df['Classification'].value_counts())

    y_test.replace({
        'Negative for intraepithelial lesion': 0,
        'HSIL': 1,
        'LSIL': 1,
        'ASC-H': 1,
        'ASC-US': 1,
        'SCC': 1
    }, inplace=True)
    print(y_test.value_counts())

    cm = me.confusion_matrix(y_test, classification)
    classes = ['Negative', 'Positive']  # Mapeamento para 0 e 1
    disp = me.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    disp.plot(include_values=True, cmap='Blues', ax=None, xticks_rotation='horizontal')
    # Modificando os rótulos do eixo x
    plt.xticks(ticks=[0, 1], labels=classes)
    # Adicionando título
    plt.title('Matriz de confusão para classificação binária com Mahalanobis')
    # Exibindo a matriz de confusão
    plt.show()
