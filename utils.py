import pandas as pd
import math as mth

#######################################################
# Method to filter information from desired image
# @param: fileName
# returns: Tuple with nucleus_x, nucleus_y and cell_id
#######################################################

def getCellData(fileName):
    df = pd.read_csv("./data/classifications.csv")
    filtered = df[df['image_filename'] == fileName]
    tuples = list(filtered[['nucleus_x', 'nucleus_y', 'cell_id']].apply(tuple, axis=1))
    return tuples

#######################################################
# Method that reads pixel array from file and returns 
# the array
# @param: fileName
# returns: Matrix matriz
#######################################################
def getMatrixPixels(fileName):
    # Abre o arquivo para leitura
    with open(fileName, 'r') as arquivo:
        # Lê a primeira linha para obter as dimensões da matriz
        dimensoes = arquivo.readline().split()
        linhas, colunas = map(int, dimensoes)

        # Inicializa a matriz com zeros
        matriz = []

        # Lê as próximas linhas para obter os valores da matriz
        for _ in range(linhas):
            linha = list(map(int, arquivo.readline().split()))
            matriz.append(linha)

    # Imprime a matriz lida do arquivo
    #print("Matriz lida do arquivo:")
    #for linha in matriz:
    #    print(linha)

    return matriz


#######################################################
# Calculate the medoide coordinate of a region 
# representing an object in an image
# @param: matriz - Matrix containing the object region
# returns: medoide
#######################################################
def calculateMedoide(matriz):
    linhas = len(matriz)
    colunas = len(matriz[0])
    soma_x, soma_y, count = 0, 0, 0
    menor_dist = 1000000

    for i in range(linhas):
        for j in range(colunas):
            if matriz[i][j] == 1:  # Verifica se o pixel é parte do objeto
                soma_x += j  # Soma as coordenadas x dos pixels do objeto
                soma_y += i  # Soma as coordenadas y dos pixels do objeto
                count += 1   # Conta a quantidade de pixels do objeto

    if count > 0:
        centroide_x = soma_x / count  # Calcula a média das coordenadas x
        centroide_y = soma_y / count  # Calcula a média das coordenadas y
        centroide = (centroide_x, centroide_y)
        print(f"Centroide: x={centroide_x}, y={centroide_y}")
    else:
        print("Nenhum pixel de objeto encontrado na matriz.")

    for i in range(linhas):
        for j in range(colunas):
            if matriz[i][j] == 1:
                dist = mth.dist([i, j], [centroide[0], centroide[1]])
                if ( dist <= menor_dist ):
                    menor_dist = dist
                    medoide_x = j
                    medoide_y = i
                    medoide = (medoide_x, medoide_y)

    

    return medoide
