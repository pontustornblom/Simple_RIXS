#fit_background_to_XAS_data_script
import numpy as np
from scipy.optimize import curve_fit

###############################################################################
# Modified Functions Without Constant Terms
###############################################################################


def func_ln(x, a, b):
    return a * np.log(b * x)

def func_negative_ln(x, a, b):
    return -a * np.log(b * x)

def func_e_to_the_power_of_x(x, a, b):
    return a * np.exp(b * x)

def func_e_to_the_power_of_negative_x(x, a, b):
    return a * np.exp(-(b * x))

def func_gaussian(x, A, mu, sigma):
    return A * np.exp(-(x - mu)**2 / (2 * sigma**2))
###############################################################################
# Updated Dictionary of Available Functions Without Constants
###############################################################################

available_functions = {
    "a*ln(b*x)": {
        "func": func_ln,
        "num_params": 2,  
        "initial_guess": [1.0, 1.0]
    },
    "-a*ln(b*x)": {
        "func": func_negative_ln,
        "num_params": 2,  
        "initial_guess": [1.0, 1.0]
    },
    "a*e^(b*x)": {
        "func": func_e_to_the_power_of_x,
        "num_params": 2,  
        "initial_guess": [1.0, 1.0]
    },
    "a*e^(-b*x)": {
        "func": func_e_to_the_power_of_negative_x,
        "num_params": 2,  
        "initial_guess": [1.0, 1.0]
    },
    "Gaussian": {
        "func": func_gaussian,
        "num_params": 3, 
        "initial_guess": [1.0, 1.0, 1.0]
    }

}

def power_factory(n):

    def power_func(x, a):
        return a*(x**n)
    return power_func

def add_power_function(n):
    key_name = f"a*x^{n}"
    available_functions[key_name] = {
        "func": power_factory(n),
        "num_params": 1,
        "initial_guess": [1.0]
    }

###############################################################################
# Polynomial Factory Without Constant Term
# For a polynomial of degree deg, we now have:
# f(x) = c_1*x + c_2*x^2 + ... + c_deg*x^deg
# So there are 'deg' parameters, no c_0.
###############################################################################

def polynomial_factory(deg):
    """
    Returns a polynomial function with no constant term:
    f(x, c_1, c_2, ..., c_deg) = sum_{i=1}^deg c_i * x^i
    """
    def poly_func(x, *coeffs):
        # coeffs = (c_1, c_2, ..., c_deg)
        # Evaluate f(x) = c_1*x^1 + c_2*x^2 + ... + c_deg*x^deg
        y = np.zeros_like(x, dtype=float)
        for i, c in enumerate(coeffs, start=1):
            y += c * x**i
        return y
    return poly_func

def add_polynomial_function(deg):
    """
    Adds a polynomial function of degree deg without a constant term.
    For example, poly_deg2 = c_1*x + c_2*x^2
    num_params = deg
    initial_guess = zeros of length deg.
    """
    key_name = f"Polynomial of degree {deg}"
    num_params = deg  # no constant term
    initial_guess = [0.0] * num_params
    available_functions[key_name] = {
        "func": polynomial_factory(deg),
        "num_params": num_params,
        "initial_guess": initial_guess
    }


def build_combined_model(selected_funcs):
    # Sum the number of parameters from all selected functions
    total_params = sum(available_functions[f]["num_params"] for f in selected_funcs)
    combined_initial_guess = []
    for f_key in selected_funcs:
        combined_initial_guess.extend(available_functions[f_key]["initial_guess"])
    
    # Add one additional parameter for the global offset
    # This offset is added after all functions have been summed.
    combined_initial_guess.append(0.0)  # initial guess for the offset
    total_params += 1  # one extra parameter for offset

    def combined_model(x, *params):
        # params includes all function parameters plus one offset at the end
        offset = params[-1]
        y = np.zeros_like(x, dtype=float)
        start = 0
        for f_key in selected_funcs:
            info = available_functions[f_key]
            n = info["num_params"]
            f_params = params[start:start+n]
            start += n
            y += info["func"](x, *f_params)
        # Add the global offset
        y += offset
        return y
    
    return combined_model, total_params, combined_initial_guess


def get_fit_data(parameters, incoming_energy_array, intensity_array):
    x_fit_combined = []
    y_fit_combined = []

    if int(parameters["number_of_energy_regions_to_fit_background_xas"]) > 0:
        for energy_region_index in range(int(parameters["number_of_energy_regions_to_fit_background_xas"])):
            index_start = np.abs(incoming_energy_array - float(parameters["background_fit_energy_start_array"][energy_region_index])).argmin()
            index_end = np.abs(incoming_energy_array - float(parameters["background_fit_energy_end_array"][energy_region_index])).argmin()
                
            if index_start > index_end:
                index_start, index_end = index_end, index_start
            
            x_fit_combined.append(incoming_energy_array[index_start : index_end])
            y_fit_combined.append(intensity_array[index_start : index_end])
            
        if len(x_fit_combined) > 1:
            x_fit = np.concatenate(x_fit_combined)
            y_fit = np.concatenate(y_fit_combined)
        else:
            x_fit = x_fit_combined[0]
            y_fit = y_fit_combined[0]
    else:
        return incoming_energy_array, intensity_array
    
    return x_fit, y_fit


def fit_background_to_XAS_data(parameters, intensity_array, incoming_energy_array):
    
    selected_functions_array = parameters["selected_functions_for_background_fit_xas_array"][0 : int(parameters["number_of_functions_to_fit_background_xas"])]

    for function_index, function in enumerate(parameters["selected_functions_for_background_fit_xas_array"][0 : int(parameters["number_of_functions_to_fit_background_xas"])]):
        if function[0:10] == "Polynomial":
            selected_functions_array[function_index] = "Polynomial of degree " + str(int(parameters["value_of_n_for_background_fit_array"][function_index]))
            n = int(parameters["value_of_n_for_background_fit_array"][function_index])
            add_polynomial_function(n)
        elif function[0:4] == "a*x^":
            selected_functions_array[function_index] = "a*x^" + str(float(parameters["value_of_n_for_background_fit_array"][function_index]))
            n = float(parameters["value_of_n_for_background_fit_array"][function_index])
            add_power_function(n)


    x_values_fit, intensity_array_fit = get_fit_data(parameters, incoming_energy_array, intensity_array)

    model, total_params, initial_guess = build_combined_model(selected_functions_array)

    coeffs, cov = curve_fit(model, x_values_fit, intensity_array_fit, p0=initial_guess)

    y_trend_values = model(incoming_energy_array, *coeffs)
    intensity_array_corrected = intensity_array - y_trend_values

    print("Selected functions:", selected_functions_array)
    print("Fitted coefficients:", coeffs)
    print("Background removed")
    return parameters, intensity_array_corrected, coeffs
