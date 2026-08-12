#adjust excitation energy for pcolormesh plot script
import numpy as np

def adjust_excitation_energy_for_pcolormesh_plot(y_values):
    y_values_halfway_points_list = []
    if len(y_values) == 1:
        y_values_halfway_points_list.append(y_values[0] - 0.5)
        y_values_halfway_points_list.append(y_values[0] + 0.5)

    elif len(y_values) == 2:
        for i in range(len(y_values) -1):
            y_values_halfway_points_list.append((y_values[i + 1] - y_values[i]) / 2 + y_values[i])
            if i == 0:
                y_values_halfway_points_list.insert(0, y_values[i] - (y_values[i + 1] - y_values[i]) / 2)
            #elif i == len(y_values) -2:   
        y_values_halfway_points_list.append(y_values[i + 1] + (y_values[i + 1] - y_values[i]) / 2)

    else:
        for i in range(len(y_values) -1):
            y_values_halfway_points_list.append((y_values[i + 1] - y_values[i]) / 2 + y_values[i])
            if i == 0:
                y_values_halfway_points_list.insert(0, y_values[i] - (y_values[i + 1] - y_values[i]) / 2)
            elif i == len(y_values) -2:   
                y_values_halfway_points_list.append(y_values[i + 1] + (y_values[i + 1] - y_values[i]) / 2)

    return np.asarray(y_values_halfway_points_list)