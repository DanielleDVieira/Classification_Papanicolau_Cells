# python3 interface.py
# img_viewer.py

import PySimpleGUI as sg
import os.path
import io
from PIL import Image, ImageTk, ImageDraw
from utils import *
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

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
    [sg.Button('Compute', key='COMPUTE'), sg.Button('Zoom In', key='ZOOM_IN')],
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
    [sg.Input(key="-7IDISF-")],
    [sg.Text(key="-8IDISF-", text="c2 - Interval: [0.1,1.0]")],
    [sg.Input(key="-9IDISF-")],
]

params_disf = [
    [sg.Text(key="-0DISF-", text="VASCO")],
    [sg.Input(key="-1DISF-")],
]

param_values = [
    [sg.Text(text="Current values:")],
    [sg.Text(text=f"Cut Size Value: {cut_size}", key="-CUTSIZEVALUE-")],
]

names=["IDISF", "DISF"]
lst = [
        [sg.Combo(names,  expand_x=True, expand_y=False, enable_events=True, default_value=names[0], readonly=True, key='-COMBO-', size=(20, 20))],
]
removeOption=["Removal by relevance", "Removal by class"]
pathCostOptions=["1:color distance", "2:gradient-cost", "3:beta norm", "4:cv tree norm", "5:sum gradient-cost", "6: sum beta norm"]

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
            [sg.Text(text="Seed removal options:")],
            [sg.Combo(removeOption, expand_x=True, expand_y=False, enable_events=True, default_value=removeOption[0], readonly=True, key='-COMBOREMOVAL-', size=(20, 20))],
            [sg.Text(key="-2IDISF-", text="Number of final superpixels:")],
            [sg.Input(key="-3IDISF-")],
            [sg.Text(key="-4IDISF-", text="Number of iterations:", visible=False)],
            [sg.Input(key="-5IDISF-", visible=False)],
            [sg.Text(text="Path-cost function:")],
            [sg.Combo(pathCostOptions, expand_x=True, expand_y=False, enable_events=True, default_value=pathCostOptions[0], readonly=True, key='-COMBOPATHCOST-', size=(20, 20))],
            [sg.Text(key="-6IDISF-", text="c1 - Interval: [0.1,1.0]", visible=False)],
            [sg.Input(key="-7IDISF-", visible=False)],
            [sg.Text(key="-8IDISF-", text="c2 - Interval: [0.1,1.0]", visible=False)],
            [sg.Input(key="-9IDISF-", visible=False)],
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
    print(event, values) 
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
            window["-COMBOREMOVAL-"].update(visible=True)
            window["-COMBOPATHCOST-"].update(visible=True)
            for i in range(len(params_disf)):
                aux = f"-{i}DISF-"
                window[aux].update(visible=False)

            for i in range(len(params_idisf)):
                aux = f"-{i}IDISF-"
                window[aux].update(visible=True)
            print("OPA")

        else: 
            window["-COMBOREMOVAL-"].update(visible=False)
            window["-COMBOPATHCOST-"].update(visible=False)

            for i in range(len(params_idisf)):
                print(type(i))
                if (i != 2) & (i != 3):
                    print(f'{i} nao eh 2 ou 3')
                    aux = f"-{i}IDISF-"
                    window[aux].update(visible=False)
                else:
                    print(f'{i} eh 2 ou 3')
                    aux = f"-{i}IDISF-"
                    window[aux].update(visible=True)

            #for i in range(len(params_disf)):
            #    aux = f"-{i}DISF-"
            #    window[aux].update(visible=True)

    elif event == "-COMBOREMOVAL-":
        remove_option = values["-COMBOREMOVAL-"]

        if remove_option == "Removal by relevance":
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

    elif event == "COMPUTE":
        # Chama a função getCellData com o nome do arquivo selecionado
        cell_information = getCellData(filename)
        
        cut_size = int(values["-CUTSIZE-"])
        window["-CUTSIZE-"].update(f"Cut Image Size: {cut_size}")

        coordinates = [(x, y) for x, y, cell_id in cell_information] 
        c_ids = [cell_id for x, y, cell_id in cell_information]
        
        print("Coordinates for", filename, ":")
        for coord in coordinates:
            print(coord)

        print("Cells id for", filename, ":")
        for ids in c_ids:
            print(ids)

        # Converta as coordenadas para o sistema de coordenadas do Pillow
        largura_imagem, altura_imagem = Image.open(filename_with_path).size
        print("Largura da imagem: ", largura_imagem)
        print("Altura da imagem: ", altura_imagem)

        # Adiciona a chamada da função colorize_coordinates após obter as coordenadas
        colorized_image_path = colorize_coordinates(filename_with_path, coordinates, "./colorCoordinates")

        print("Imagem colorizada salva em:", colorized_image_path)

        # [recortar_e_salvar_imagem(filename_with_path, x, y, cell_id, cut_size, "./recorteImg") for x, y, cell_id in cell_information]
        resulting_coordinates = [recortar_e_salvar_imagem(filename_with_path, x, y, cell_id, cut_size, "./recorteImg") for x, y, cell_id in cell_information]
        print("New coordinates:")
        for coord in resulting_coordinates:
            print(coord)

    elif event == "ZOOM_IN":
        plt.imshow(image)
        plt.show()

window.close()
os.system('rm -r recorteImg && rm -r colorCoordinates')
