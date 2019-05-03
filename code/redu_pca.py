import numpy as np
from numpy import mean
import pandas as pd
import sys
import os
import csv
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn

PATH_TO_COMPONENT_MATRIX = "./component_matrix.csv" #Eigenvectors
PATH_TO_ORIGINAL_PCA = "./original_pca.csv" #original PCA matrix of the original files


### Given a file input occurrence table, creates the eigen vectors file defined above PATH_TO_COMPONENT_MATRIX, and PCA project of these files PATH_TO_ORIGINAL_PCA
def calculate_master_projection(input_file_occurrences_table):
    with open(input_file_occurrences_table, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter = "\t") 
        file_list = next(reader)
    useable_cols = len(file_list)
    
    compound_location = file_list.index("LibraryID") #finding the proper column for compound list

    if compound_location == 0:
        col_range = np.arange(2, useable_cols)
    else:
        col_range = np.arange(0, useable_cols-2)


    compound_list = np.loadtxt(input_file_occurrences_table, dtype = str, delimiter = "\t", usecols = compound_location, skiprows = 1)
    df = pd.read_csv(input_file_occurrences_table, sep = "\t", usecols = col_range, header = 0, skip_blank_lines = True)

    new_matrix = df.values.T #align so that the "features" are column headers

    pca = PCA(n_components = 5) #creating the instance
    pca.fit(new_matrix) #fitting the data 

    component_matrix = pca.components_ #principle components / vectors
    dataframe1 = pd.DataFrame(data = component_matrix.transpose())
    dataframe1['filename'] = compound_list
    dataframe1.to_csv(r"component_matrix.csv")
    
    sklearn_output = pca.transform(new_matrix) #using sklearn to calculate the output
    
    dataframe2 = pd.DataFrame(data = sklearn_output)
    dataframe2.to_csv(r"original_pca.csv")

### Given a new file occurrence table, creates a projection of the new data along with the old data and saves as a png output
def project_new_data(input_file_occurrences_table, output_png):
    new_matrix = np.array([]) 
    file_list = []

    component_matrix = pd.read_csv(PATH_TO_COMPONENT_MATRIX, sep = ",")
    old_compound_list = list(component_matrix['filename']) #list of all compounds found in the OG data

    component_matrix = component_matrix.drop(['Unnamed: 0', 'filename'], axis = 1) 
    component_matrix = component_matrix.transpose()
    component_matrix.columns = old_compound_list
   #the point at which I realized I'm a messy coder and you have a boatload of patience
   #figuring out the filenames for the new data
    with open(input_file_occurrences_table, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter = "\t")  
        file_list = next(reader)
 
        compound_location = file_list.index("LibraryID") #finding the proper column for compound list
        useable_cols = len(file_list)

        if compound_location == 0:
            col_range = np.arange(2, useable_cols)
        else:
            col_range = np.arange(0, useable_cols-2)

    new_compound_list = np.loadtxt(input_file_occurrences_table, dtype = str, delimiter = "\t", skiprows = 1, usecols = compound_location)
    
    new_filtered = [item for item in new_compound_list if item in old_compound_list]


    df = pd.read_csv(input_file_occurrences_table, sep = "\t", usecols = col_range, skip_blank_lines = True)
    df = df.transpose()
    df.columns = new_compound_list
    df = df[new_filtered]
    
    
    we_dont_care, final_matrix = component_matrix.align(df, join = 'left', axis = 1, fill_value = 0)

    final_matrix = final_matrix.values
    mean_matrix = mean(final_matrix.T, axis = 1)

    C = final_matrix - mean_matrix

    
    component_matrix = component_matrix.values.T
    we_dont_care = we_dont_care.T
      
    visualize_stuff = C.dot(we_dont_care) #manually calculating the output for projection
    
    dataframe4 = pd.read_csv(PATH_TO_ORIGINAL_PCA, sep = ",")
    dataframe3 = pd.DataFrame(data = visualize_stuff)
    
    scatterplot_new = seaborn.scatterplot(0, 1, data = dataframe3, marker = 'x') 
    scatterplot_original = seaborn.scatterplot('0','1', data = dataframe4)
    figure = scatterplot_new.get_figure()
    figure.savefig(output_png)
    

def main():
    input_global_file_occurrences_table = sys.argv[1]
    output_png = "output_merged_png.png"

    calculate_master_projection(input_global_file_occurrences_table)
    project_new_data(input_global_file_occurrences_table, output_png)

if __name__ == "__main__":
    main()