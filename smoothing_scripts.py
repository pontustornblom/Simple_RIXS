#smoothing_scripts
import numpy as np

def bin_intensity_array(intensity_array, bin_size):
    if bin_size == "":
        print("Bin size can not be empty. The spectra was not changed")
        return intensity_array
    
    bin_size = int(bin_size)
    if bin_size == 0:
        print("Bin size can not be zero. The spectra was not changed")
        return intensity_array

    intensity_array = np.array(intensity_array)
    num_full_bins = len(intensity_array) // bin_size
    truncated_array = intensity_array[:num_full_bins * bin_size]
    
    reshaped_array = truncated_array.reshape(-1, bin_size)

    binned_array = reshaped_array.sum(axis=1)
    
    # Check if there are remaining points that were not binned
    if len(intensity_array) % bin_size != 0:
        remaining_points = intensity_array[num_full_bins * bin_size:]
        last_bin_value = remaining_points.sum()
        binned_array = np.append(binned_array, last_bin_value)
    
    return binned_array


def bin_energy_array(energy_array, bin_size):
    if bin_size == "":
        print("Bin size can not be empty. The spectra was not changed")
        return energy_array
    
    bin_size = int(bin_size)
    if bin_size == 0:
        print("Bin size can not be zero. The spectra was not changed")
        return energy_array

    energy_array = np.array(energy_array)
    num_full_bins = len(energy_array) // bin_size
    truncated_array = energy_array[:num_full_bins * bin_size]
    
    reshaped_array = truncated_array.reshape(-1, bin_size)

    binned_array = reshaped_array.mean(axis=1)
    
    # Check if there are remaining points that were not binned
    if len(energy_array) % bin_size != 0:
        remaining_points = energy_array[num_full_bins * bin_size:]
        last_bin_value = remaining_points.mean()
        binned_array = np.append(binned_array, last_bin_value)
    
    return binned_array
