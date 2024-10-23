import numpy as np
import cv2

def binary_repr(pixel, width=8):
    return format(pixel, f'0{width}b')

def dna_encode(pixel):
    dna_map = {
        '00': 'A',
        '01': 'C',
        '10': 'G',
        '11': 'T'
    }
    binary_pixel = binary_repr(pixel)
    dna_sequence = ''.join(dna_map[binary_pixel[i:i+2]] for i in range(0, 8, 2))
    return dna_sequence

def dna_decode(dna_sequence):
    dna_map = {
        'A': '00',
        'C': '01',
        'G': '10',
        'T': '11'
    }
    binary_string = ''.join(dna_map[nuc] for nuc in dna_sequence)
    return int(binary_string, 2)

def logistic_map(x, mu, size):
    sequence = []
    for _ in range(size):
        x = mu * x * (1 - x)
        sequence.append(x)
    return sequence

def chebyshev_map(x, w, size):
    sequence = []
    for _ in range(size):
        x = np.cos(w * np.arccos(x))
        sequence.append(x)
    return sequence

def encrypt_image(image, a0, b0, mu_a, mu_b, z0, q0, wz, wq):
    M, N, C = image.shape
    encrypted_channels = []

    for channel in cv2.split(image):
        logistic_seq_r = logistic_map(a0, mu_a, M)
        logistic_seq_c = logistic_map(b0, mu_b, N)

        sorted_r_idx = np.argsort(logistic_seq_r)
        sorted_c_idx = np.argsort(logistic_seq_c)

        confused_channel = channel[sorted_r_idx, :]
        confused_channel = confused_channel[:, sorted_c_idx]

        dna_encoded = np.vectorize(dna_encode)(confused_channel)

        chebyshev_seq_q = chebyshev_map(q0, wq, M * N * 4)
        chebyshev_diffusion = [(int(abs(q) * 10) % 15 + 1) for q in chebyshev_seq_q]

        def nucleotide_transform(nucleotide, step):
            dna_map = 'ACGT'
            index = dna_map.index(nucleotide)
            return dna_map[(index + step) % 4]

        dna_flat = ''.join(dna_encoded.flatten())
        diffused_dna = ''.join(
            nucleotide_transform(nuc, step) for nuc, step in zip(dna_flat, chebyshev_diffusion)
        )

        decoded_pixels = [
            dna_decode(diffused_dna[i:i+4]) for i in range(0, len(diffused_dna), 4)
        ]
        diffused_channel = np.array(decoded_pixels, dtype=np.uint8).reshape(M, N)

        encrypted_channels.append(diffused_channel)

    encrypted_image = cv2.merge(encrypted_channels)
    return encrypted_image

def process_and_encrypt_image(input_image_path, output_image_path, encryption_params):
    image = cv2.imread(input_image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Image not found at path: {input_image_path}")

    a0 = encryption_params.get('a0', 0.4)
    b0 = encryption_params.get('b0', 0.5)
    mu_a = encryption_params.get('mu_a', 3.99)
    mu_b = encryption_params.get('mu_b', 3.99)
    z0 = encryption_params.get('z0', 0.6)
    q0 = encryption_params.get('q0', 0.7)
    wz = encryption_params.get('wz', 2.0)
    wq = encryption_params.get('wq', 2.0)

    encrypted_image = encrypt_image(image, a0, b0, mu_a, mu_b, z0, q0, wz, wq)

    cv2.imwrite(output_image_path, encrypted_image)
    print(f"Encrypted image saved to {output_image_path}")

if __name__ == "__main__":
    encryption_parameters = {
        'a0': 0.4,
        'b0': 0.5,
        'mu_a': 3.99,
        'mu_b': 3.99,
        'z0': 0.6,
        'q0': 0.7,
        'wz': 2.0,
        'wq': 2.0
    }

    input_img_path = 'image.jpg'    
    output_img_path = 'encrypted_image.jpg' 

    try:
        process_and_encrypt_image(input_img_path, output_img_path, encryption_parameters)
    except Exception as e:
        print(f"An error occurred: {e}")
