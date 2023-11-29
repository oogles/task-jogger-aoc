def split_lines(input_data):
    
    return input_data.splitlines()


def int_lines(input_data):
    
    return [int(line) for line in input_data.splitlines()]


def split_commas(input_data):
    
    return input_data.split(',')


def int_commas(input_data):
    
    return [int(value) for value in input_data.split(',')]
