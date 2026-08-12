#find_elastic_peak_maximum_script
import numpy as np

def find_elastic_peak_maximum(parameters, y_values, approximate_channel_of_elastic_peak):
    #highest_intensity_channel = np.where(y_values[approximate_channel_of_elastic_peak- int(parameters["channels_above_and_below_for_finding_elastic"]) : approximate_channel_of_elastic_peak+ int(parameters["channels_above_and_below_for_finding_elastic"]) + 1] > 0, y_values[approximate_channel_of_elastic_peak- int(parameters["channels_above_and_below_for_finding_elastic"]) : approximate_channel_of_elastic_peak+ int(parameters["channels_above_and_below_for_finding_elastic"]) + 1], np.inf).argmax()
    #highest_intensity = y_values[highest_intensity_channel]
    
    highest_intensity = max(y_values[approximate_channel_of_elastic_peak- int(parameters["channels_above_and_below_for_finding_elastic"]) : approximate_channel_of_elastic_peak+ int(parameters["channels_above_and_below_for_finding_elastic"]) + 1])
    highest_intensity_channel = (y_values[approximate_channel_of_elastic_peak- int(parameters["channels_above_and_below_for_finding_elastic"]) : approximate_channel_of_elastic_peak+ int(parameters["channels_above_and_below_for_finding_elastic"]) + 1]).argmax()

    highest_intensity_channel = highest_intensity_channel + approximate_channel_of_elastic_peak- int(parameters["channels_above_and_below_for_finding_elastic"])
    #highest_intensity=0
    #highest_intensity_channel=0
    #for channel in range(approximate_channel_of_elastic_peak- int(parameters["channels_above_and_below_for_finding_elastic"]), approximate_channel_of_elastic_peak+ int(parameters["channels_above_and_below_for_finding_elastic"]) + 1):
    #    if y_values[channel] >= highest_intensity:
    #        highest_intensity= y_values[channel]
    #        highest_intensity_channel= channel

    return highest_intensity, highest_intensity_channel
