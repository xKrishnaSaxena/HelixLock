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
def decrypt_image(encrypted_image, a0, b0, mu_a, mu_b, z0, q0, wz, wq):
    M, N, _ = encrypted_image.shape
    decrypted_channels = []

    for channel in cv2.split(encrypted_image):
        chebyshev_sequence_z = chebyshev_map(z0, wz, M * N * 4)
        chebyshev_sequence_q = chebyshev_map(q0, wq, M * N * 4)

        chebyshev_diffusion = [(int(abs(q) * 10) % 15 + 1) for q in chebyshev_sequence_q]

        def nucleotide_transform(nucleotide, steps):
            dna_map = 'ACGT'
            index = dna_map.index(nucleotide)
            return dna_map[(index - steps) % 4]

        dna_encoded_channel = ''.join([
            nucleotide_transform(dna, int(steps))
            for dna, steps in zip(''.join(np.vectorize(dna_encode)(channel).flatten()), chebyshev_diffusion)
        ])

        decrypted_channel = np.array([
            dna_decode(dna_encoded_channel[i:i + 4])
            for i in range(0, len(dna_encoded_channel), 4)
        ]).reshape(M, N)

        decrypted_channels.append(decrypted_channel)

    decrypted_image = cv2.merge(decrypted_channels)

    logistic_sequence_r = logistic_map(a0, mu_a, M)
    logistic_sequence_c = logistic_map(b0, mu_b, N)

    sorted_r_idx = np.argsort(logistic_sequence_r)
    sorted_c_idx = np.argsort(logistic_sequence_c)

    original_image = decrypted_image[np.argsort(sorted_r_idx), :]
    original_image = original_image[:, np.argsort(sorted_c_idx)]
    print(f"Decrypted image saved to decrypted_image.jpg")

    return original_image

if __name__ == "__main__":
    image = cv2.imread('encrypted_image.jpg', cv2.IMREAD_COLOR)
    a0, b0 = 0.4, 0.5
    mu_a, mu_b = 3.99, 3.99
    z0, q0 = 0.6, 0.7
    wz, wq = 2.0, 2.0

    decrypted_image = decrypt_image(image, a0, b0, mu_a, mu_b, z0, q0, wz, wq)
    cv2.imwrite('decrypted_image.jpg', decrypted_image)