# python3 interface.py
# img_viewer.py

import PySimpleGUI as sg
import os.path
import io
from PIL import Image, ImageTk, ImageDraw
from utils import *

# Default cut size is 100
cut_size = 100

def resize_image(image, scale_factor):
    width, height = image.size
    new_width = int(width* scale_factor)
    new_height = int(height * scale_factor)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    return resized_image

def convert_to_base64(image):
    with io.BytesIO() as output:
        image.save(output, format='PNG')
    return base64.b64encode(output.getvalue()).decode('utf-8')

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
    [sg.Button('Zoom In', key='ZOOM_IN'), sg.Button('Zoom Out', key='ZOOM_OUT')],
    [sg.Button('Compute', key='COMPUTE')],
]

params_image_cut = [
    [sg.Text(text="Size (px) of image cut")],
    [sg.Input(key="-CUTSIZE-")],
]


params_idisf= [
   [sg.Text(key="-0IDISF-", text="Number of Seeds", visible=True)],
   [sg.Input(key="-1IDISF-", visible=True)],
]

params_disf = [
    [sg.Text(key="-0DISF-", text="VASCO", visible=False)],
    [sg.Input(key="-1DISF-", visible=False)],
]

param_values = [
    [sg.Text(text="Current values:")],
    [sg.Text(text=f"Cut Size Value: {cut_size}", key="-CUTSIZEVALUE-")],
]

names=["IDISF", "DISF"]
lst = [
        [sg.Combo(names,  expand_x=True, expand_y=False, enable_events=True, default_value=names[0], readonly=True, key='-COMBO-', size=(20, 20))],
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
        sg.VSeparator(),
        [(params_image_cut), (lst)],
        sg.Column(params_idisf, vertical_alignment='top'),
        sg.Column(params_disf, vertical_alignment='top'),
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
            current_scale = 1.0
            image.thumbnail((400, 400))  # Ajuste o tamanho conforme necessário
            photo_img = ImageTk.PhotoImage(image)

            window["-IMAGE-"].update(data=photo_img)
        except:
            pass
    elif event == "-COMBO-":
        alg = values['-COMBO-']
        if alg == "IDISF":
            for i in range(len(params_disf)):
                aux = f"-{i}DISF-"
                window[aux].update(visible=False)

            for i in range(len(params_idisf)):
                aux = f"-{i}IDISF-"
                window[aux].update(visible=True)
            print("OPA")
        else: 
            for i in range(len(params_idisf)):
                aux = f"-{i}IDISF-"
                window[aux].update(visible=False)

            for i in range(len(params_disf)):
                aux = f"-{i}DISF-"
                window[aux].update(visible=True)

    elif event == "COMPUTE":
        # Chama a função getCellData com o nome do arquivo selecionado
        cell_information = getCellData(filename)
        
        cut_size = int(values["-CUTSIZE-"])
        window["-CUTSIZEVALUE-"].update(f"Cut Image Size: {cut_size}")

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
        resulting_coordinates = [recortar_e_salvar_imagem(filename_with_path, x, y, 100, "./recorteImg") for x, y in coordinates]
            print("New coordinates:")
            for coord in resulting_coordinates:
                print(coord)
        



    elif event == "ZOOM_IN":
        current_scale *= 1.1
        resized_image = resize_image(image, current_scale)
        photo_img = ImageTk.PhotoImage(resized_image)
        window["-IMAGE-"].update(data=photo_img)

    elif event == "ZOOM_OUT":
        current_scale *= 0.9
        resized_image = resize_image(image, current_scale)
        photo_img = ImageTk.PhotoImage(resized_image)
        window["-IMAGE-"].update(data=photo_img)

window.close()
os.system('rm -r recorteImg && rm -r colorCoordinates')
