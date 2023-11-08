import pandas as pd

#################################################
# Method to filter information from desired image
# @param: fileName
# returns: Tuple with nucleus_x and nucleus_y
#################################################

def getCoordinates(fileName):
    df = pd.read_csv("data/classifications.csv")
    filtered = df[df['image_filename'] == fileName]
    tuples = list(filtered[['nucleus_x', 'nucleus_y']].apply(tuple, axis=1))
    return tuples
