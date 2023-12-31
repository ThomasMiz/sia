from tp4.tools import *
from tp4.Kohonen.kohonen import *
import json
import time
import matplotlib.pyplot as plt
import seaborn as sns

countries, titles, country_data = csv_to_dict("../europe.csv")
standardized_country_data = standardize_data(country_data)

with open('kohonen-config.json') as f:
    config = json.load(f)

# Acceder a los valores del archivo JSON
k_config = config['k']
initial_radius = config['initial_radius']
initial_eta = config['initial_eta']
max_iterations = config['max_iterations']
initialize_weights_random = config['initialize_weights_random']
print_neighborhood = config['print_neighborhood']
print_iteration_results = config['print_iteration_results']
print_final_results = config['print_final_results']
threshold = config['threshold']
decay_factor = config['decay_factor']

kohonen = Kohonen(standardized_country_data, k_config, initial_radius, initial_eta, max_iterations, initialize_weights_random,
                  print_neighborhood, print_iteration_results, print_final_results, threshold, decay_factor)
result = kohonen.start()

# kohonen.create_neighborhood_gif()

print(standardized_country_data)

kohonen.plot_heatmap_u_matrix()
kohonen.plot_heatmap_final_entries(False)
kohonen.plot_heatmap_final_entries(True)
for k in range(len(next(iter(country_data.values())))):
    kohonen.plot_heatmap_variable(k, titles[k + 1])