import pandas as pd

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
