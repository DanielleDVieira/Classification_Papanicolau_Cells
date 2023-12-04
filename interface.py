# python3 interface.py
# img_viewer.py

from utils import *
from PIL import Image, ImageTk, ImageDraw
from os import listdir
from os.path import isfile, join
from skimage import measure
import PySimpleGUI as sg
import os.path
import io
import math as mth
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys


# Default cut size is 100
cut_size = 100

def colorize_coordinates(image_path, coordinates, output_folder):
    # Abre a imagem
    image = Image.open(image_path)

    # Cria um objeto ImageDraw para desenhar na imagem
    draw = ImageDraw.Draw(image)

    # Define a cor ciano (RGB: 0, 255, 255)
    ciano = (0, 255, 255)

    # Itera sobre as coordenadas e altera os pixels para a cor ciano
    for x, y in coordinates:
        for i in range(-2, 3):
            for j in range(-2, 3):
                new_x = x + i
                new_y = y + j
                
                # Verifica se as novas coordenadas estão dentro dos limites da imagem
                if 0 <= new_x < image.width and 0 <= new_y < image.height:
                    draw.point((new_x, new_y), fill=ciano)
        

    # Obtém o nome do arquivo sem a extensão e adiciona "_colorized" ao nome
    filename_without_extension = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = f"{filename_without_extension}_colorized.png"

    # Cria o caminho completo para o arquivo de saída
    output_path = os.path.join(output_folder, output_filename)

    # Salva a imagem colorizada na pasta de saída
    image.save(output_path)

    return output_path

def recortar_e_salvar_imagem(nome_imagem, x, y, cells_id, dimensao_recorte, pasta_destino):
    # Abre a imagem em modo RGB
    im = Image.open(nome_imagem)

    # Obtém apenas o nome do arquivo a partir do caminho completo
    filename = os.path.basename(nome_imagem)

    # Obtém as dimensões da imagem original
    width, height = im.size

    # Calcula as coordenadas para o recorte com base na coordenada central e na dimensão desejada
    left = x - dimensao_recorte // 2
    top = y - dimensao_recorte // 2
    right = left + dimensao_recorte
    bottom = top + dimensao_recorte

    # Garante que as coordenadas não ultrapassem os limites da imagem
    left = max(0, left)
    top = max(0, top)
    right = min(width, right)
    bottom = min(height, bottom)

    # Cria o recorte da imagem
    im_recortada = im.crop((left, top, right, bottom))

    # Cria o caminho para a pasta de destino
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    # Gera o nome do arquivo para alvar
    nome_arquivo = os.path.join(pasta_destino, f"{cells_id}.png")

    # Salva a imagem recortada na pasta de destino
    im_recortada.save(nome_arquivo)

    # Calcula a nova coordenada na imagem recortada correspondente à coordenada original
    nova_coordenada_x = x - left
    nova_coordenada_y = y - top

    return nova_coordenada_x, nova_coordenada_y

# First the window layout in 2 columns

file_list_column = [
    [
        sg.Text("Image Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]

# For now will only show the name of the file that was chosen
image_viewer_column = [
    [sg.Text("Choose an image from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
    # [sg.Button('Zoom In', key='ZOOM_IN'), sg.Button('Zoom Out', key='ZOOM_OUT')],
    [sg.Button('Compute', key='COMPUTE'), sg.Button('Compute All', key='COMPUTE_ALL'), sg.Button('Zoom In', key='ZOOM_IN')],
]

params_image_cut = [
    [sg.Text(text="Size (px) of image cut")],
    [sg.Input(key="-CUTSIZE-")],
]


#params_idisf= [
#   [sg.Text(key="-0IDISF-", text="Number of Seeds", visible=True)],
#   [sg.Input(key="-1IDISF-", visible=True)],
#]

#params_disf = [
#    [sg.Text(key="-0DISF-", text="VASCO", visible=False)],
#    [sg.Input(key="-1DISF-", visible=False)],
#]

params_idisf = [
    [sg.Text(key="-0IDISF-", text="Number of init GRID seeds (>= 0)")],
    [sg.Input(key="-1IDISF-")],
    [sg.Text(key="-2IDISF-", text="Number of final superpixels")],
    [sg.Input(key="-3IDISF-")],
    [sg.Text(key="-4IDISF-", text="Number of iterations")],
    [sg.Input(key="-5IDISF-")],
    [sg.Text(key="-6IDISF-", text="c1 - Interval: [0.1,1.0]")],
    [sg.Slider(range=(0, 1), default_value=0, resolution=0.01, expand_x=True, enable_events=True, orientation='horizontal', key='-7IDISF-')],
    #[sg.Input(key="-7IDISF-")],
    [sg.Text(key="-8IDISF-", text="c2 - Interval: [0.1,1.0]")],
    [sg.Slider(range=(0, 1), default_value=0, resolution=0.01, expand_x=True, enable_events=True, orientation='horizontal', key='-9IDISF-')],
    #[sg.Input(key="-9IDISF-")],
]

params_disf = [
    [sg.Text(key="-0DISF-", text="VASCO")],
    [sg.Input(key="-1DISF-")],
]

param_values = [
    [sg.Text(text="Current values:")],
    [sg.Text(text=f"Cut Size Value: {cut_size}", key="-CUTSIZEVALUE-")],
]

names=["Select Segmentation Algorithm", "IDISF", "DISF"]
lst = [
        [sg.Combo(names,  expand_x=True, expand_y=False, enable_events=True, default_value=names[0], readonly=True, key='-COMBO-', size=(20, 20))],
]
removeOption=["Select Removal" , "1:Removal by class", "2:Removal by relevance"]
pathCostOptions=["Select Path Cost", "1:color distance", "2:gradient-cost", "3:beta norm", "4:cv tree norm", "5:sum gradient-cost", "6: sum beta norm"]

# ----- Full layout -----
#layout = [
#    [
#        sg.Column(file_list_column),
#        sg.VSeperator(),
#        sg.Column(image_viewer_column),
#        sg.VSeparator(),
#        [(params_image_cut), (lst)],
#        sg.Column(params_idisf, vertical_alignment='top'),
#        sg.Column(params_disf, vertical_alignment='top'),
#    ]
#]

# Layout atualizado com a única coluna para exibir os parâmetros correspondentes à escolha no dropdown
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeparator(),
        sg.Column([
            [sg.Text(text="Size (px) of image cut:")],
            [sg.Input(key="-CUTSIZE-")],
            [sg.Text(text="Method for segmentation:")],
            [sg.Combo(names, expand_x=True, expand_y=False, enable_events=True, default_value=names[0], readonly=True, key='-COMBO-', size=(20, 20))],
            [sg.Text(key="-0IDISF-", text="Number of init GRID seeds (>= 0)")],
            [sg.Input(key="-1IDISF-")],
            [sg.Text(key='-1DROP-', text="Seed removal options:")],
            [sg.Combo(removeOption, expand_x=True, expand_y=False, enable_events=True, default_value=removeOption[0], readonly=True, key='-COMBOREMOVAL-', size=(20, 20))],
            [sg.Text(key="-2IDISF-", text="Number of final superpixels:")],
            [sg.Input(key="-3IDISF-")],
            [sg.Text(key="-4IDISF-", text="Number of iterations:", visible=False)],
            [sg.Input(key="-5IDISF-", visible=False)],
            [sg.Text(key='-2DROP-', text="Path-cost function:")],
            [sg.Combo(pathCostOptions, expand_x=True, expand_y=False, enable_events=True, default_value=pathCostOptions[0], readonly=True, key='-COMBOPATHCOST-', size=(20, 20))],
            [sg.Text(key="-6IDISF-", text="c1 - Interval: [0.1,1.0]", visible=False)],
            #[sg.Input(key="-7IDISF-", visible=False)],
            [sg.Slider(range=(0.01, 1), default_value=0, resolution=0.01, expand_x=True, enable_events=True, orientation='horizontal', key='-7IDISF-')],
            [sg.Text(key="-8IDISF-", text="c2 - Interval: [0.1,1.0]", visible=False)],
            #[sg.Input(key="-9IDISF-", visible=False)],
            [sg.Slider(range=(0.01, 1), default_value=0, resolution=0.01, expand_x=True, enable_events=True, orientation='horizontal', key='-9IDISF-')],
            [sg.Text(key="-0DISF-", text="VASCO", visible=False)],
            [sg.Input(key="-1DISF-", visible=False)],
        ]),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

os.system("mkdir recorteImg && mkdir colorCoordinates")
window = sg.Window("Image Viewer", layout, resizable=True)

# Run the Event Loop
while True:
    event, values = window.read()
    # print(event, values) 
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".png", ".jpg"))
        ]
        window["-FILE LIST-"].update(fnames)

    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename_with_path = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )

            # Obtém apenas o nome do arquivo a partir do caminho completo
            filename = os.path.basename(filename_with_path)

            #print(f"filename with path {filename_with_path}")
            #print(f"Just filename: {filename}")

            window["-TOUT-"].update(filename_with_path)

            image = Image.open(filename_with_path)
            image.thumbnail((400, 400))  # Ajuste o tamanho conforme necessário
            photo_img = ImageTk.PhotoImage(image)

            window["-IMAGE-"].update(data=photo_img)
        except:
            pass
    elif event == "-COMBO-":
        alg = values['-COMBO-']
        if alg == "IDISF":
            window["-1DROP-"].update(visible=True)
            window["-2DROP-"].update(visible=True)
            window["-COMBOREMOVAL-"].update(visible=True)
            window["-COMBOPATHCOST-"].update(visible=True)
            for i in range(len(params_disf)):
                aux = f"-{i}DISF-"
                window[aux].update(visible=False)

            for i in range(len(params_idisf)):
                aux = f"-{i}IDISF-"
                window[aux].update(visible=True)

        else: 
            window["-1DROP-"].update(visible=False)
            window["-2DROP-"].update(visible=False)
            window["-COMBOREMOVAL-"].update(visible=False)
            window["-COMBOPATHCOST-"].update(visible=False)

            for i in range(len(params_idisf)):
                if (i != 0) & (i != 1) & (i != 2) & (i != 3):
                    aux = f"-{i}IDISF-"
                    window[aux].update(visible=False)
                else:
                    aux = f"-{i}IDISF-"
                    window[aux].update(visible=True)

            #for i in range(len(params_disf)):
            #    aux = f"-{i}DISF-"
            #    window[aux].update(visible=True)

    elif event == "-COMBOREMOVAL-":
        remove_option = values["-COMBOREMOVAL-"]

        if remove_option == "2:Removal by relevance":
            # Nao aparecer o campo de numero de iteracoes se a remocao for por relevancia
            window["-4IDISF-"].update(visible=False)
            window["-5IDISF-"].update(visible=False)
            window["-2IDISF-"].update(visible=True)
            window["-3IDISF-"].update(visible=True)
        else:
            # Nao aparecer o campo de numero de superpixels finais se a remocao for por classe
            window["-2IDISF-"].update(visible=False)
            window["-3IDISF-"].update(visible=False)
            window["-4IDISF-"].update(visible=True)
            window["-5IDISF-"].update(visible=True)

    elif event == "-COMBOPATHCOST-":
        functionsPathCost = values["-COMBOPATHCOST-"]

        if (functionsPathCost == "1:color distance") | (functionsPathCost == "6: sum beta norm"):
            # Nao mostrar parametros das funcoes do path-cost se as funcoes forem 1 ou 6
            window["-6IDISF-"].update(visible=False)
            window["-7IDISF-"].update(visible=False)
            window["-8IDISF-"].update(visible=False)
            window["-9IDISF-"].update(visible=False)
        else:
            window["-6IDISF-"].update(visible=True)
            window["-7IDISF-"].update(visible=True)
            window["-8IDISF-"].update(visible=True)
            window["-9IDISF-"].update(visible=True)
    elif event == "COMPUTE_ALL":
        onlyfiles = [f for f in listdir(values["-FOLDER-"]) if isfile(join(values["-FOLDER-"], f))]
        for i in range(len(onlyfiles)):
            filename = os.path.basename(onlyfiles[i])
            filename_with_path = os.path.join(
                values["-FOLDER-"], onlyfiles[i]
            )
            # Chama a função getCellData com o nome do arquivo selecionado
            cell_information = getCellData(filename)
            filename_without_png = filename.split(".")[0]

            alg = values['-COMBO-']

            seeds = int(values['-1IDISF-'])
            window["-1IDISF-"].update(f"{seeds}")

            idisfCall = ""
            disfCall = ""

            if alg == "IDISF":
                idisfCall += f"./src/iDISF/bin/iDISF_demo --i ./recorteImg/{filename_without_png}/*.png --n0 {seeds} --obj_markers 1 --o ./recorteImg/{filename_without_png}/segmented/* --xseeds xCoord --yseeds yCoord " 

                try:
                    remove_option = int(values["-COMBOREMOVAL-"].split(':')[0])
                    idisfCall += f"--rem {remove_option} "
                except: continue
                try:
                    functionsPathCost = int(values["-COMBOPATHCOST-"].split(':')[0])
                    idisfCall += f"--f {functionsPathCost} "
                except: continue

                if remove_option == 2: 
                    super_pixel = int(values['-3IDISF-'])
                    window["-3IDISF-"].update(f"{super_pixel}")
                    idisfCall += f"--nf {super_pixel} "
                else: 
                    n_iterations = int(values['-5IDISF-'])
                    window["-5IDISF-"].update(f"{n_iterations}")
                    idisfCall += f"--it {n_iterations} "

                if (functionsPathCost != 1) & (functionsPathCost != 6):
                    c1 = float(values['-7IDISF-'])
                    window["-7IDISF-"].update(f"{c1}")
                    idisfCall += f"--c1 {c1} "

                    c2 = float(values['-9IDISF-'])
                    window["-9IDISF-"].update(f"{c2}")
                    idisfCall += f"--c2 {c2} "

                    print(f'C1: {c1} \t C2: {c2}')

                cut_size = int(values["-CUTSIZE-"])
                window["-CUTSIZE-"].update(f"{cut_size}")

            else:
                super_pixel = int(values['-3IDISF-'])
                window["-3IDISF-"].update(f"{super_pixel}")

                disfCall = f"./src/DISF/bin/DISF_demo ./recorteImg/{filename_without_png}/*.png {seeds} {super_pixel} ./recorteImg/{filename_without_png}/segmented/*.png" 

            coordinates = [(x, y) for x, y, cell_id in cell_information] 
            c_ids = [cell_id for x, y, cell_id in cell_information]

            # Converta as coordenadas para o sistema de coordenadas do Pillow
            largura_imagem, altura_imagem = Image.open(filename_with_path).size

            # Adiciona a chamada da função colorize_coordinates após obter as coordenadas
            colorized_image_path = colorize_coordinates(filename_with_path, coordinates, "./colorCoordinates")

            print("Imagem colorizada salva em:", colorized_image_path)

            # Recortar imagens conforme dimensao informado na interface e coordenadas de cada celula da imagem
            resulting_coordinates = [recortar_e_salvar_imagem(filename_with_path, x, y, cell_id, cut_size, f"./recorteImg/{filename_without_png}") for x, y, cell_id in cell_information]

            os.system(f"mkdir ./recorteImg/{filename_without_png}/segmented")

            idisfCopy = idisfCall
            disfCopy = disfCall
            nameFileMatrix = f"./recorteImg/{filename_without_png}/segmented/*.txt"
            copyNameFileMatrix = nameFileMatrix

            medoides = []  # Vetor para armazenar os medoides
            # Creating folder to save all metrics that will be calculated
            metrics_path = f"./data"
            metrics_file = f"{metrics_path}/metrics.csv"            
            os.system(f"mkdir {metrics_path}")
            
            result = ""
            # Substituir o id da celula e coordenadas para segmentacao
            for id, coord in zip(c_ids, resulting_coordinates):
                disfCopy = disfCopy.replace('*', str(id))
                idisfCopy = idisfCopy.replace('*', str(id))
                idisfCopy = idisfCopy.replace('xCoord', str(coord[0]))
                idisfCopy = idisfCopy.replace('yCoord', str(coord[1]))

                copyNameFileMatrix = copyNameFileMatrix.replace('*', str(id))

                if alg == "IDISF": 
                    os.system(idisfCopy)  
                else: 
                    os.system(disfCopy)

                # Armazenar matriz de pixels de fundo e objeto lidos do arquivo txt após segmentação
                matriz = getMatrixPixels(copyNameFileMatrix)
                # Calcular o medoide do objeto conforme matriz
                medoide = calculateMedoide(matriz)
                # Adicionar o medoide ao vetor de medoides
                medoides.append(medoide)

                print(f"Medoide: x={medoide[0]}, y={medoide[1]} - coordCSV: {coord}")
                dist = mth.dist(medoide, coord)
                area = cv2.countNonZero(np.ravel(matriz))
                contornos = measure.find_contours(np.asarray(matriz))
                maior_contorno = max(contornos, key=len)
                perimetro = len(maior_contorno)
                compacidade = (4 * np.pi * area) / (perimetro ** 2)
                rotulado = measure.label(np.asarray(matriz))
                propriedades = measure.regionprops(rotulado)
                maior_regiao = max(propriedades, key=lambda x: x.area)
                excentricidade = maior_regiao.eccentricity

                result += f"{id};({medoide[0]},{medoide[1]});({coord[0]},{coord[1]});{dist};{area};{perimetro};{compacidade};{excentricidade}\n"


                # Voltar *, xCoord e yCoord para serem substituidos pelos novos dados
                idisfCopy = idisfCall
                disfCopy = disfCall
                copyNameFileMatrix = nameFileMatrix


            file_metrics = open(metrics_file, "a")
            file_metrics.write("ID;MedoideCalculado;CoordCSV;DistanciaDoCentro;Area;Perimetro;Compacidade;Excentricidade\n")
            file_metrics.write(result)
            file_metrics.close()

    elif event == "COMPUTE":        
        # Chama a função getCellData com o nome do arquivo selecionado
        cell_information = getCellData(filename)
        filename_without_png = filename.split(".")[0]

        alg = values['-COMBO-']

        seeds = int(values['-1IDISF-'])
        window["-1IDISF-"].update(f"{seeds}")

        idisfCall = ""
        disfCall = ""

        if alg == "IDISF":
            idisfCall += f"./src/iDISF/bin/iDISF_demo --i ./recorteImg/{filename_without_png}/*.png --n0 {seeds} --obj_markers 1 --o ./recorteImg/{filename_without_png}/segmented/* --xseeds xCoord --yseeds yCoord " 

            try:
                remove_option = int(values["-COMBOREMOVAL-"].split(':')[0])
                idisfCall += f"--rem {remove_option} "
            except: continue
            try:
                functionsPathCost = int(values["-COMBOPATHCOST-"].split(':')[0])
                idisfCall += f"--f {functionsPathCost} "
            except: continue

            if remove_option == 2: 
                super_pixel = int(values['-3IDISF-'])
                window["-3IDISF-"].update(f"{super_pixel}")
                idisfCall += f"--nf {super_pixel} "
            else: 
                n_iterations = int(values['-5IDISF-'])
                window["-5IDISF-"].update(f"{n_iterations}")
                idisfCall += f"--it {n_iterations} "

            if (functionsPathCost != 1) & (functionsPathCost != 6):
                c1 = float(values['-7IDISF-'])
                window["-7IDISF-"].update(f"{c1}")
                idisfCall += f"--c1 {c1} "

                c2 = float(values['-9IDISF-'])
                window["-9IDISF-"].update(f"{c2}")
                idisfCall += f"--c2 {c2} "

                print(f'C1: {c1} \t C2: {c2}')

            cut_size = int(values["-CUTSIZE-"])
            window["-CUTSIZE-"].update(f"{cut_size}")

        else:
            super_pixel = int(values['-3IDISF-'])
            window["-3IDISF-"].update(f"{super_pixel}")

            disfCall = f"./src/DISF/bin/DISF_demo ./recorteImg/{filename_without_png}/*.png {seeds} {super_pixel} ./recorteImg/{filename_without_png}/segmented/*.png" 

        coordinates = [(x, y) for x, y, cell_id in cell_information] 
        c_ids = [cell_id for x, y, cell_id in cell_information]
        
        #print("Coordinates for", filename, ":")
        #for coord in coordinates:
        #    print(coord)

        #print("Cells id for", filename, ":")
        #for ids in c_ids:
        #    print(ids)

        # Converta as coordenadas para o sistema de coordenadas do Pillow
        largura_imagem, altura_imagem = Image.open(filename_with_path).size
        #print("Largura da imagem: ", largura_imagem)
        #print("Altura da imagem: ", altura_imagem)

        # Adiciona a chamada da função colorize_coordinates após obter as coordenadas
        colorized_image_path = colorize_coordinates(filename_with_path, coordinates, "./colorCoordinates")

        print("Imagem colorizada salva em:", colorized_image_path)

        # Recortar imagens conforme dimensao informado na interface e coordenadas de cada celula da imagem
        resulting_coordinates = [recortar_e_salvar_imagem(filename_with_path, x, y, cell_id, cut_size, f"./recorteImg/{filename_without_png}") for x, y, cell_id in cell_information]
        #print("New coordinates:")
        #for coord in resulting_coordinates:
        #    print(coord)

        os.system(f"mkdir ./recorteImg/{filename_without_png}/segmented")

        idisfCopy = idisfCall
        disfCopy = disfCall
        nameFileMatrix = f"./recorteImg/{filename_without_png}/segmented/*.txt"
        copyNameFileMatrix = nameFileMatrix

        medoides = []  # Vetor para armazenar os medoides


        # Creating folder to save all metrics that will be calculated
        metrics_path = f"./data"
        metrics_file = f"{metrics_path}/metrics.csv"            
        os.system(f"mkdir {metrics_path}")


        result = ""
        # Substituir o id da celula e coordenadas para segmentacao
        for id, coord in zip(c_ids, resulting_coordinates):
            disfCopy = disfCopy.replace('*', str(id))
            idisfCopy = idisfCopy.replace('*', str(id))
            idisfCopy = idisfCopy.replace('xCoord', str(coord[0]))
            idisfCopy = idisfCopy.replace('yCoord', str(coord[1]))

            copyNameFileMatrix = copyNameFileMatrix.replace('*', str(id))

            if alg == "IDISF": 
                os.system(idisfCopy)  
            else: 
                os.system(disfCopy)

            # Armazenar matriz de pixels de fundo e objeto lidos do arquivo txt após segmentação
            matriz = getMatrixPixels(copyNameFileMatrix)
            # Calcular o medoide do objeto conforme matriz
            medoide = calculateMedoide(matriz)
            # Adicionar o medoide ao vetor de medoides
            medoides.append(medoide)

            print(f"Medoide: x={medoide[0]}, y={medoide[1]} - coordCSV: {coord}")
            dist = mth.dist(medoide, coord)
            area = cv2.countNonZero(np.ravel(matriz))
            contornos = measure.find_contours(np.asarray(matriz))
            maior_contorno = max(contornos, key=len)
            perimetro = len(maior_contorno)
            compacidade = (4 * np.pi * area) / (perimetro ** 2)
            rotulado = measure.label(np.asarray(matriz))
            propriedades = measure.regionprops(rotulado)
            maior_regiao = max(propriedades, key=lambda x: x.area)
            excentricidade = maior_regiao.eccentricity

            result += f"{id};({medoide[0]},{medoide[1]});({coord[0]},{coord[1]});{dist};{area};{perimetro};{compacidade};{excentricidade}\n"


            # Voltar *, xCoord e yCoord para serem substituidos pelos novos dados
            idisfCopy = idisfCall
            disfCopy = disfCall
            copyNameFileMatrix = nameFileMatrix


        file_metrics = open(metrics_file, "a")
        file_metrics.write("ID;MedoideCalculado;CoordCSV;DistanciaDoCentro;Area;Perimetro;Compacidade;Excentricidade\n")
        file_metrics.write(result)
        file_metrics.close()

    elif event == "ZOOM_IN":
        plt.imshow(image)
        plt.show()

window.close()
os.system(f"rm {metrics_path}")