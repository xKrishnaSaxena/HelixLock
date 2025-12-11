import numpy as np
import cv2

def binary_repr(pixel, width=8):
    binary_str = bin(pixel)[2:]
    return binary_str.zfill(width)

def dna_encode(pixel):
    dna_map = {
        '00': 'A',
        '01': 'C',
        '10': 'G',
        '11': 'T'
    }
    binary_pixel = binary_repr(pixel)
    dna_sequence = ""
    for i in range(0, 8, 2):
        two_bit_segment = binary_pixel[i:i + 2]
        dna_base = dna_map[two_bit_segment]
        dna_sequence += dna_base

    return dna_sequence

def dna_decode(dna):
    dna_map = {
        'A': '00',
        'C': '01',
        'G': '10',
        'T': '11'
    }
    binary_string = ""
    for nucleotide in dna:
        binary_segment = dna_map[nucleotide]
        binary_string += binary_segment
    decimal_value = int(binary_string, 2)
    return decimal_value


def logistic_map(x, mu, size):
    sequence = []
    for i in range(size):
        x = mu * x * (1 - x)
        sequence.append(x)
    return sequence

def chebyshev_map(x, w, size):
    sequence = []
    for i in range(size):
        x = np.cos(w * np.arccos(x))
        sequence.append(x)
    return sequence

def process_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        print("Error: Image not found.")
        return

    height, width, channels = image.shape
    with open("image_dna_output.txt", "w") as file:

        for i in range(height):
            for j in range(width):
                for c in range(channels):
                    pixel_value = image[i, j, c]
                    dna_sequence = dna_encode(pixel_value)
                    file.write(f" Pixel ({i}, {j}, {c}): {pixel_value} -> {dna_sequence} ")
                file.write("\n")



if __name__ == "__main__":
    image_path = 'image.jpg'
    process_image(image_path)
