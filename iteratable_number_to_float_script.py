#iteratable_number_to_float_script

def iteratable_number_to_float(iteratable_number):
    iteratable_file_number_length= len(iteratable_number)
    if iteratable_file_number_length!= 1:
        number_of_zeros_in_iteratable_number= 0
        for number in range(iteratable_file_number_length):
            if iteratable_number[number]==0:
                number_of_zeros_in_iteratable_number+=1
        if number_of_zeros_in_iteratable_number == iteratable_file_number_length:
            iteratable_file_number_int = 0
        else:
            iteratable_file_number_int= float(iteratable_number[number_of_zeros_in_iteratable_number:])
    else:
        iteratable_file_number_int= float(iteratable_number)
    return iteratable_file_number_int