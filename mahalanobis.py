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

# Função para calcular a distância de Mahalanobis para a classe
def mahalanobis_dist(sample, mean, cov):
    return mahalanobis(sample, mean, cov)

def MahalanobisTrain():
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

    """# Scatter Plot"""

    df['bethesda_system'].unique()

    scc = df[df['bethesda_system'] == 'SCC']
    neg = df[df['bethesda_system'] == 'Negative for intraepithelial lesion']
    lsi = df[df['bethesda_system'] == 'LSIL']
    hsi = df[df['bethesda_system'] == 'HSIL']
    ash = df[df['bethesda_system'] == 'ASC-H']
    asu = df[df['bethesda_system'] == 'ASC-US']

    plt.figure(figsize=(10,6))

    scatter0 = plt.scatter(scc['Area'], scc['Excentricidade'], c='#ff0000', s=2, alpha=1, label='SCC')
    scatter1 = plt.scatter(neg['Area'], neg['Excentricidade'], c='#000000', s=2, alpha=1, label='Negative')
    scatter2 = plt.scatter(lsi['Area'], lsi['Excentricidade'], c='#00ff00', s=2, alpha=1, label='LSIL')
    scatter3 = plt.scatter(hsi['Area'], hsi['Excentricidade'], c='#0000ff', s=2, alpha=1, label='HSIL')
    scatter4 = plt.scatter(ash['Area'], ash['Excentricidade'], c='#440154', s=2, alpha=1, label='ASC-H')
    scatter5 = plt.scatter(asu['Area'], asu['Excentricidade'], c='#00ffff', s=2, alpha=1, label='ASC-US')

    plt.legend(title='Classes', loc="upper right", markerscale=2)
    plt.xlabel("Área", size=15)
    plt.ylabel("Excentricidade", size=15)
    plt.tight_layout()
    plt.show()

    Counter(list(df['bethesda_system']))

    """# Train test split binary"""

    print(scc.head())

    sccFeatures = scc[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    negFeatures = neg[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    lsiFeatures = lsi[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    hsiFeatures = hsi[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    ashFeatures = ash[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    asuFeatures = asu[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]

    X_train0, X_test0, y_train0, y_test0 = train_test_split(sccFeatures, scc['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train1, X_test1, y_train1, y_test1 = train_test_split(negFeatures, neg['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train2, X_test2, y_train2, y_test2 = train_test_split(lsiFeatures, lsi['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train3, X_test3, y_train3, y_test3 = train_test_split(hsiFeatures, hsi['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train4, X_test4, y_train4, y_test4 = train_test_split(ashFeatures, ash['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train5, X_test5, y_train5, y_test5 = train_test_split(asuFeatures, asu['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)

    X_train_neg = X_train1
    X_test_neg = X_test1
    y_train_neg = y_train1
    y_test_neg = y_test1

    X_train_positive = pd.concat([X_train0, X_train2, X_train3, X_train4, X_train5], ignore_index=True)
    X_test_positive = pd.concat([X_test0, X_test2, X_test3, X_test4, X_test5], ignore_index=True)
    y_train_positive = pd.concat([y_train0, y_train2, y_train3, y_train4, y_train5], ignore_index=True)
    y_test_positive = pd.concat([y_test0, y_test2, y_test3, y_test4, y_test5], ignore_index=True)

    y_test = pd.concat([y_test_neg, y_test_positive], ignore_index=True)

    features_train_neg = X_train_neg.iloc[:, 1:5]
    features_train_positive = X_train_positive.iloc[:, 1:5]

    features_test_neg = X_test_neg.iloc[:, 1:5].to_numpy()
    features_test_positive = X_test_positive.iloc[:, 1:5].to_numpy()

    features_test = np.concatenate((features_test_neg, features_test_positive))
    features_test_id = pd.concat([X_test_neg, X_test_positive], ignore_index=True)

    # Calcular a matriz de covariância para a classe negativa
    cov_neg = np.cov(features_train_neg, rowvar=False)
    mean_neg = np.mean(features_train_neg, axis=0)
    cov_positive = np.cov(features_train_positive, rowvar=False)
    mean_positive = np.mean(features_train_positive, axis=0)

    # Calcular a distância de Mahalanobis para cada amostra de teste
    distances_neg = [mahalanobis_dist(sample, mean_neg, cov_neg) for sample in features_test]
    distances_positive = [mahalanobis_dist(sample, mean_positive, cov_positive) for sample in features_test]

    """#Salvando os Dados de Treino"""
    malahanobis_train_values = "./data/mahalanobis_train_data/binary"

    # Salvar cov_neg como CSV
    np.savetxt(f'{malahanobis_train_values}/cov_neg.csv', cov_neg, delimiter=',')
    # Salvar mean_neg como CSV
    mean_neg.to_csv(f'{malahanobis_train_values}/mean_neg.csv', header=False)
    # Salvar cov_positive como CSV
    np.savetxt(f'{malahanobis_train_values}/cov_positive.csv', cov_positive, delimiter=',')
    # Salvar mean_positive como CSV
    mean_positive.to_csv(f'{malahanobis_train_values}/mean_positive.csv', header=False)

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

    acuracia = me.accuracy_score(y_test, classification)
    print("Acurácia:", acuracia)

    precisao = me.precision_score(y_test, classification)
    print("Precisão:", precisao)

    sensibilidade = me.recall_score(y_test, classification)
    print("Sensibilidade (Revocação):", sensibilidade)

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



    """# Train test split Six Classes """
    print(scc.head())

    sccFeatures = scc[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    negFeatures = neg[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    lsiFeatures = lsi[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    hsiFeatures = hsi[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    ashFeatures = ash[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    asuFeatures = asu[['cell_id', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]

    X_train0, X_test0, y_train0, y_test0 = train_test_split(sccFeatures, scc['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train1, X_test1, y_train1, y_test1 = train_test_split(negFeatures, neg['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train2, X_test2, y_train2, y_test2 = train_test_split(lsiFeatures, lsi['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train3, X_test3, y_train3, y_test3 = train_test_split(hsiFeatures, hsi['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train4, X_test4, y_train4, y_test4 = train_test_split(ashFeatures, ash['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    X_train5, X_test5, y_train5, y_test5 = train_test_split(asuFeatures, asu['bethesda_system'], test_size=0.2, train_size=0.8, shuffle=True, random_state=42)
    
    """ #SCC Class"""
    X_train_scc = X_train0
    X_test_scc = X_test0
    y_train_scc = y_train0
    y_test_scc = y_test0

    features_train_scc = X_train_scc.iloc[:, 1:5]
    features_test_scc = X_test_scc.iloc[:, 1:5].to_numpy()

    # Calcular a matriz de covariância para a classe SCC
    cov_scc = np.cov(features_train_scc, rowvar=False)
    mean_scc = np.mean(features_train_scc, axis=0)

    """ #Neg Class """
    X_train_neg = X_train1
    X_test_neg = X_test1
    y_train_neg = y_train1
    y_test_neg = y_test1

    features_train_neg = X_train_neg.iloc[:, 1:5]
    features_test_neg = X_test_neg.iloc[:, 1:5].to_numpy()

    # Calcular a matriz de covariância para a classe NEG
    cov_neg = np.cov(features_train_neg, rowvar=False)
    mean_neg = np.mean(features_train_neg, axis=0)

    """ #LSI Class """
    X_train_lsi = X_train2
    X_test_lsi = X_test2
    y_train_lsi = y_train2
    y_test_lsi = y_test2

    features_train_lsi = X_train_lsi.iloc[:, 1:5]
    features_test_lsi = X_test_lsi.iloc[:, 1:5].to_numpy()

    # Calcular a matriz de covariância para a classe LSI
    cov_lsi = np.cov(features_train_lsi, rowvar=False)
    mean_lsi = np.mean(features_train_lsi, axis=0)

    """ #HSI Class """
    X_train_hsi = X_train3
    X_test_hsi = X_test3
    y_train_hsi = y_train3
    y_test_hsi = y_test3

    features_train_hsi = X_train_hsi.iloc[:, 1:5]
    features_test_hsi = X_test_hsi.iloc[:, 1:5].to_numpy()

    # Calcular a matriz de covariância para a classe HSI
    cov_hsi = np.cov(features_train_hsi, rowvar=False)
    mean_hsi = np.mean(features_train_hsi, axis=0)

    """ #ASH Class """
    X_train_ash = X_train4
    X_test_ash = X_test4
    y_train_ash = y_train4
    y_test_ash = y_test4

    features_train_ash = X_train_ash.iloc[:, 1:5]
    features_test_ash = X_test_ash.iloc[:, 1:5].to_numpy()

    # Calcular a matriz de covariância para a classe ASH
    cov_ash = np.cov(features_train_ash, rowvar=False)
    mean_ash = np.mean(features_train_ash, axis=0)

    """ #ASU Class """
    X_train_asu = X_train5
    X_test_asu = X_test5
    y_train_asu = y_train5
    y_test_asu = y_test5

    features_train_asu = X_train_asu.iloc[:, 1:5]
    features_test_asu = X_test_asu.iloc[:, 1:5].to_numpy()

    """ #Y_test """
    y_test = pd.concat([y_test_scc, y_test_neg, y_test_lsi, y_test_hsi, y_test_ash, y_test_asu], ignore_index=True)


    # Calcular a matriz de covariância para a classe ASU
    cov_asu = np.cov(features_train_asu, rowvar=False)
    mean_asu = np.mean(features_train_asu, axis=0)

    """ #Grouping all classes """
    features_test = np.concatenate((features_test_scc, features_test_neg, features_test_lsi, features_test_hsi, features_test_ash, features_test_asu))
    features_test_id = pd.concat([X_test_scc, X_test_neg, X_test_lsi, X_test_hsi, X_test_ash, X_test_asu], ignore_index=True)

    # Calcular a distância de Mahalanobis para cada amostra de teste
    distances_scc = [mahalanobis_dist(sample, mean_scc, cov_scc) for sample in features_test]
    distances_neg = [mahalanobis_dist(sample, mean_neg, cov_neg) for sample in features_test]
    distances_lsi = [mahalanobis_dist(sample, mean_lsi, cov_lsi) for sample in features_test]
    distances_hsi = [mahalanobis_dist(sample, mean_hsi, cov_hsi) for sample in features_test]
    distances_ash = [mahalanobis_dist(sample, mean_ash, cov_ash) for sample in features_test]
    distances_asu = [mahalanobis_dist(sample, mean_asu, cov_asu) for sample in features_test]

    """#Salvando os Dados de Treino"""
    malahanobis_train_values = "./data/mahalanobis_train_data/six_classes"

    # Salvar scc como CSV
    np.savetxt(f'{malahanobis_train_values}/cov_scc.csv', cov_scc, delimiter=',')
    mean_scc.to_csv(f'{malahanobis_train_values}/mean_scc.csv', header=False)

    # Salvar neg como CSV
    np.savetxt(f'{malahanobis_train_values}/cov_neg.csv', cov_neg, delimiter=',')
    mean_neg.to_csv(f'{malahanobis_train_values}/mean_neg.csv', header=False)

    # Salvar lsi como CSV
    np.savetxt(f'{malahanobis_train_values}/cov_lsi.csv', cov_lsi, delimiter=',')
    mean_lsi.to_csv(f'{malahanobis_train_values}/mean_lsi.csv', header=False)

    # Salvar hsi como CSV
    np.savetxt(f'{malahanobis_train_values}/cov_hsi.csv', cov_hsi, delimiter=',')
    mean_hsi.to_csv(f'{malahanobis_train_values}/mean_hsi.csv', header=False)

    # Salvar ash como CSV
    np.savetxt(f'{malahanobis_train_values}/cov_ash.csv', cov_ash, delimiter=',')
    mean_ash.to_csv(f'{malahanobis_train_values}/mean_ash.csv', header=False)

    # Salvar asu como CSV
    np.savetxt(f'{malahanobis_train_values}/cov_asu.csv', cov_asu, delimiter=',')
    mean_asu.to_csv(f'{malahanobis_train_values}/mean_asu.csv', header=False)


    df['Classification'] = -1
    classification = []

    size = len(X_test_scc) + len(X_test_neg) + len(X_test_lsi) + len(X_test_hsi) + len(X_test_ash) + len(X_test_asu)
 
    for i in range(size):
        if distances_scc[i] < distances_neg[i] and distances_scc[i] < distances_lsi[i] and distances_scc[i] < distances_hsi[i] and distances_scc[i] < distances_ash[i] and distances_scc[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['cell_id']
            df.loc[df['cell_id'] == id, 'Classification'] = 1
            classification.append(1)
        elif distances_neg[i] < distances_scc[i] and distances_neg[i] < distances_lsi[i] and distances_neg[i] < distances_hsi[i] and distances_neg[i] < distances_ash[i] and distances_neg[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['cell_id']
            df.loc[df['cell_id'] == id, 'Classification'] = 0
            classification.append(0)
        elif distances_lsi[i] < distances_scc[i] and distances_lsi[i] < distances_neg[i] and distances_lsi[i] < distances_hsi[i] and distances_lsi[i] < distances_ash[i] and distances_lsi[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['cell_id']
            df.loc[df['cell_id'] == id, 'Classification'] = 2
            classification.append(2)
        elif distances_hsi[i] < distances_scc[i] and distances_hsi[i] < distances_neg[i] and distances_hsi[i] < distances_lsi[i] and distances_hsi[i] < distances_ash[i] and distances_hsi[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['cell_id']
            df.loc[df['cell_id'] == id, 'Classification'] = 3
            classification.append(3)
        elif distances_ash[i] < distances_scc[i] and distances_ash[i] < distances_neg[i] and distances_ash[i] < distances_lsi[i] and distances_ash[i] < distances_hsi[i] and distances_ash[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['cell_id']
            df.loc[df['cell_id'] == id, 'Classification'] = 4
            classification.append(4)
        elif distances_asu[i] < distances_scc[i] and distances_asu[i] < distances_neg[i] and distances_asu[i] < distances_lsi[i] and distances_asu[i] < distances_hsi[i] and distances_asu[i] < distances_ash[i]:
            id = features_test_id.iloc[i]['cell_id']
            df.loc[df['cell_id'] == id, 'Classification'] = 5
            classification.append(5)
            
            
    print(df['Classification'].value_counts())

    y_test.replace({
        'Negative for intraepithelial lesion': 0,
        'SCC': 1,
        'LSIL': 2,
        'HSIL': 3,
        'ASC-H': 4,
        'ASC-US': 5,
    }, inplace=True)


    acuracia = me.accuracy_score(y_test, classification)
    print("Acurácia:", acuracia)

    precisao = me.precision_score(y_test, classification, average='micro')
    print("Precisão:", precisao)

    sensibilidade = me.recall_score(y_test, classification, average='micro')
    print("Sensibilidade (Revocação):", sensibilidade)

    cm = me.confusion_matrix(y_test, classification)
    classes = ['Negative', 'SCC', 'LSIL', 'HSIL', 'ASC-H', 'ASC-US']  # Mapeamento para 0 e 1
    disp = me.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    disp.plot(include_values=True, cmap='Blues', ax=None, xticks_rotation='horizontal')
    # Modificando os rótulos do eixo x
    plt.xticks(ticks=[0, 1, 2, 3, 4, 5], labels=classes)
    # Adicionando título
    plt.title('Matriz de confusão para classificação binária com Mahalanobis')
    # Exibindo a matriz de confusão
    plt.show()

# Função que classifica as células da imagem com a distância de Mahalanobis
def MahalanobisBinaryClassifier(filename):
    """# Open DF"""
    df = pd.read_csv("./data/classifications.csv")
    metrics = pd.read_csv("./data/metrics.csv", sep=';')

    print(metrics.head())
    """# Getting features from image """
    features_test_id = metrics[['ID', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    features_test = features_test_id.iloc[:, 1:5].to_numpy()
    features = df[df['image_filename'] == filename]
    y_test = features[['bethesda_system']]
    
    """#Salvando os Dados de Treino"""
    malahanobis_values = "./data/mahalanobis_train_data/binary"

    # Carregar cov_neg do CSV
    cov_neg = np.loadtxt(f'{malahanobis_values}/cov_neg.csv', delimiter=',')
    mean_neg = pd.read_csv(f'{malahanobis_values}/mean_neg.csv', header=None, index_col=0)[1]
    mean_neg = pd.Series(mean_neg)

    # Carregar cov_pos do CSV
    cov_positive = np.loadtxt(f'{malahanobis_values}/cov_positive.csv', delimiter=',')
    mean_positive = pd.read_csv(f'{malahanobis_values}/mean_positive.csv', header=None, index_col=0)[1]
    mean_positive = pd.Series(mean_positive)
   
    # Calcular a distância de Mahalanobis para cada amostra de teste
    distances_neg = [mahalanobis_dist(sample, mean_neg, cov_neg) for sample in features_test]
    distances_positive = [mahalanobis_dist(sample, mean_positive, cov_positive) for sample in features_test]
    print(f"ALOO {len(distances_neg)}")
    df['Classification'] = -1
    classification = []

    for i in range(len(distances_neg)):
        if distances_neg[i] > distances_positive[i]:
            id = features_test_id.iloc[i]['ID']
            df.loc[df['cell_id'] == id, 'Classification'] = 1
            classification.append(1)
        else:
            id = features_test_id.iloc[i]['ID']
            df.loc[df['cell_id'] == id, 'Classification'] = 0       
            classification.append(0)

    print(len(features_test_id))


    y_test.replace({
        'Negative for intraepithelial lesion': 0,
        'HSIL': 1,
        'LSIL': 1,
        'ASC-H': 1,
        'ASC-US': 1,
        'SCC': 1
    }, inplace=True)
    print(f"{y_test.value_counts()}")

    acuracia = me.accuracy_score(y_test, classification)
    print("Acurácia:", acuracia)

    precisao = me.precision_score(y_test, classification, zero_division=0)
    print("Precisão:", precisao)

    sensibilidade = me.recall_score(y_test, classification, zero_division=0)
    print("Sensibilidade (Revocação):", sensibilidade)

    cm = me.confusion_matrix(y_test, classification)
    classes = ['Negative', 'Positive']  # Mapeamento para 0 e 1
    disp = me.ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(include_values=True, cmap='Blues', ax=None, xticks_rotation='horizontal')
    # Adicionando título
    plt.title('Matriz de confusão para classificação binária com Mahalanobis')
    # Exibindo a matriz de confusão
    plt.show()

# Função que classifica as células da imagem com a distância de Mahalanobis
def MahalanobisSixClassifier(filename):
    """# Open DF"""
    df = pd.read_csv("./data/classifications.csv")
    metrics = pd.read_csv("./data/metrics.csv", sep=';')

    print(metrics.head())
    """# Getting features from image """
    features_test_id = metrics[['ID', 'Area', 'Perimetro', 'Compacidade', 'Excentricidade']]
    features_test = features_test_id.iloc[:, 1:5].to_numpy()
    features = df[df['image_filename'] == filename]
    y_test = features[['bethesda_system']]
    
    """#Salvando os Dados de Treino"""
    malahanobis_values = "./data/mahalanobis_train_data/six_classes"

    # Carregar cov_scc do CSV
    cov_scc = np.loadtxt(f'{malahanobis_values}/cov_scc.csv', delimiter=',')
    mean_scc = pd.read_csv(f'{malahanobis_values}/mean_scc.csv', header=None, index_col=0)[1]
    mean_scc = pd.Series(mean_scc)

    # Carregar cov_neg do CSV
    cov_neg = np.loadtxt(f'{malahanobis_values}/cov_neg.csv', delimiter=',')
    mean_neg = pd.read_csv(f'{malahanobis_values}/mean_neg.csv', header=None, index_col=0)[1]
    mean_neg = pd.Series(mean_neg)

    # Carregar cov_lsi do CSV
    cov_lsi = np.loadtxt(f'{malahanobis_values}/cov_lsi.csv', delimiter=',')
    mean_lsi = pd.read_csv(f'{malahanobis_values}/mean_lsi.csv', header=None, index_col=0)[1]
    mean_lsi = pd.Series(mean_lsi)

    # Carregar cov_hsi do CSV
    cov_hsi = np.loadtxt(f'{malahanobis_values}/cov_hsi.csv', delimiter=',')
    mean_hsi = pd.read_csv(f'{malahanobis_values}/mean_hsi.csv', header=None, index_col=0)[1]
    mean_hsi = pd.Series(mean_hsi)

    # Carregar cov_ash do CSV
    cov_ash = np.loadtxt(f'{malahanobis_values}/cov_ash.csv', delimiter=',')
    mean_ash = pd.read_csv(f'{malahanobis_values}/mean_ash.csv', header=None, index_col=0)[1]
    mean_ash = pd.Series(mean_ash)

    # Carregar cov_asu do CSV
    cov_asu = np.loadtxt(f'{malahanobis_values}/cov_asu.csv', delimiter=',')
    mean_asu = pd.read_csv(f'{malahanobis_values}/mean_asu.csv', header=None, index_col=0)[1]
    mean_asu = pd.Series(mean_asu)
   
    # Calcular a distância de Mahalanobis para cada amostra de teste
    distances_scc = [mahalanobis_dist(sample, mean_scc, cov_scc) for sample in features_test]
    distances_neg = [mahalanobis_dist(sample, mean_neg, cov_neg) for sample in features_test]
    distances_lsi = [mahalanobis_dist(sample, mean_lsi, cov_lsi) for sample in features_test]
    distances_hsi = [mahalanobis_dist(sample, mean_hsi, cov_hsi) for sample in features_test]
    distances_ash = [mahalanobis_dist(sample, mean_ash, cov_ash) for sample in features_test]
    distances_asu = [mahalanobis_dist(sample, mean_asu, cov_asu) for sample in features_test]

    df['Classification'] = -1
    classification = []

    size = len(features_test)
 
    for i in range(size):
        if distances_scc[i] < distances_neg[i] and distances_scc[i] < distances_lsi[i] and distances_scc[i] < distances_hsi[i] and distances_scc[i] < distances_ash[i] and distances_scc[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['ID']
            df.loc[df['cell_id'] == id, 'Classification'] = 1
            classification.append(1)
        elif distances_neg[i] < distances_scc[i] and distances_neg[i] < distances_lsi[i] and distances_neg[i] < distances_hsi[i] and distances_neg[i] < distances_ash[i] and distances_neg[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['ID']
            df.loc[df['cell_id'] == id, 'Classification'] = 0
            classification.append(0)
        elif distances_lsi[i] < distances_scc[i] and distances_lsi[i] < distances_neg[i] and distances_lsi[i] < distances_hsi[i] and distances_lsi[i] < distances_ash[i] and distances_lsi[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['ID']
            df.loc[df['cell_id'] == id, 'Classification'] = 2
            classification.append(2)
        elif distances_hsi[i] < distances_scc[i] and distances_hsi[i] < distances_neg[i] and distances_hsi[i] < distances_lsi[i] and distances_hsi[i] < distances_ash[i] and distances_hsi[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['ID']
            df.loc[df['cell_id'] == id, 'Classification'] = 3
            classification.append(3)
        elif distances_ash[i] < distances_scc[i] and distances_ash[i] < distances_neg[i] and distances_ash[i] < distances_lsi[i] and distances_ash[i] < distances_hsi[i] and distances_ash[i] < distances_asu[i]:
            id = features_test_id.iloc[i]['ID']
            df.loc[df['cell_id'] == id, 'Classification'] = 4
            classification.append(4)
        elif distances_asu[i] < distances_scc[i] and distances_asu[i] < distances_neg[i] and distances_asu[i] < distances_lsi[i] and distances_asu[i] < distances_hsi[i] and distances_asu[i] < distances_ash[i]:
            id = features_test_id.iloc[i]['ID']
            df.loc[df['cell_id'] == id, 'Classification'] = 5
            classification.append(5)

    print(len(features_test_id))

    y_test.replace({
        'Negative for intraepithelial lesion': 0,
        'SCC': 1,
        'LSIL': 2,
        'HSIL': 3,
        'ASC-H': 4,
        'ASC-US': 5,
    }, inplace=True)
    print(f"{y_test.value_counts()}")

    acuracia = me.accuracy_score(y_test, classification)
    print("Acurácia:", acuracia)

    precisao = me.precision_score(y_test, classification, average='micro')
    print("Precisão:", precisao)

    sensibilidade = me.recall_score(y_test, classification, average='micro')
    print("Sensibilidade (Revocação):", sensibilidade)

    cm = me.confusion_matrix(y_test, classification)
    classes = ['Negative', 'SCC', 'LSIL', 'HSIL', 'ASC-H', 'ASC-US']  # Mapeamento para 0 1 2 3 4 5
    #disp = me.ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
    #disp.plot(include_values=True, cmap='Blues', ax=None, xticks_rotation='horizontal')
    disp = me.ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(include_values=True, cmap='Blues', ax=None, xticks_rotation='horizontal')
    # Modificando os rótulos do eixo x
    #plt.xticks(ticks=[0, 1], labels=classes)
    # Adicionando título
    plt.title('Matriz de confusão para classificação binária com Mahalanobis')
    # Exibindo a matriz de confusão
    plt.show()