# python3 interface.py
# img_viewer.py

import PySimpleGUI as sg
import os.path
import io
from PIL import Image, ImageTk
from utils import *

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
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

window = sg.Window("Image Viewer", layout, resizable=True)

# Run the Event Loop
while True:
    event, values = window.read()
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

            # Chama a função getCoordinates com o nome do arquivo selecionado
            coordinates = getCoordinates(filename)
            
            print("Coordinates for", filename, ":")
            for coord in coordinates:
                print(coord)
            
            image = Image.open(filename_with_path)
            current_scale = 1.0
            image.thumbnail((400, 400))  # Ajuste o tamanho conforme necessário
            photo_img = ImageTk.PhotoImage(image)

            window["-IMAGE-"].update(data=photo_img)
        except:
            pass
    
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
