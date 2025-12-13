from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://helixlock.onrender.com","http://localhost:5173","https://helixlock.stelliform.xyz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def dna_encode(pixel):
    dna_map = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
    binary_pixel = np.binary_repr(pixel, width=8)
    return ''.join([dna_map[binary_pixel[i:i + 2]] for i in range(0, 8, 2)])

def dna_decode(dna):
    dna_map = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
    return int(''.join([dna_map[nucleotide] for nucleotide in dna]), 2)

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

def process_encrypt(image, params):
    M, N, _ = image.shape
    encrypted_channels = []

    # Generate Chaotic Sequences
    logistic_sequence_r = logistic_map(params['a0'], params['mu_a'], M)
    logistic_sequence_c = logistic_map(params['b0'], params['mu_b'], N)
    sorted_r_idx = np.argsort(logistic_sequence_r)
    sorted_c_idx = np.argsort(logistic_sequence_c)

    chebyshev_sequence_q = chebyshev_map(params['q0'], params['wq'], M * N * 4)
    chebyshev_diffusion = [(int(abs(q) * 10) % 15 + 1) for q in chebyshev_sequence_q]

    for channel in cv2.split(image):
        # Confusion
        confused_channel = channel[sorted_r_idx, :]
        confused_channel = confused_channel[:, sorted_c_idx]

        # DNA Encoding
        dna_encoded_image = np.vectorize(dna_encode)(confused_channel)

        # Diffusion
        flat_dna = ''.join(dna_encoded_image.flatten())

        # Optimization: Pre-calculate map for speed
        dna_lookup = 'ACGT'

        # Using list comp for transformation
        diffused_dna_list = []
        for dna, steps in zip(flat_dna, chebyshev_diffusion):
            idx = dna_lookup.index(dna)
            diffused_dna_list.append(dna_lookup[(idx + steps) % 4])
        diffused_dna = ''.join(diffused_dna_list)

        # DNA Decoding to pixels
        diffused_channel = np.array([
            dna_decode(diffused_dna[i:i + 4])
            for i in range(0, len(diffused_dna), 4)
        ]).reshape(M, N)

        encrypted_channels.append(diffused_channel.astype(np.uint8))

    return cv2.merge(encrypted_channels)

def process_decrypt(image, params):
    M, N, _ = image.shape
    decrypted_channels = []

    chebyshev_sequence_q = chebyshev_map(params['q0'], params['wq'], M * N * 4)
    chebyshev_diffusion = [(int(abs(q) * 10) % 15 + 1) for q in chebyshev_sequence_q]
    dna_lookup = 'ACGT'

    for channel in cv2.split(image):
        # Encode to DNA
        dna_encoded_input = np.vectorize(dna_encode)(channel)
        flat_dna_input = ''.join(dna_encoded_input.flatten())

        # Reverse Diffusion
        undiffused_dna_list = []
        for dna, steps in zip(flat_dna_input, chebyshev_diffusion):
            idx = dna_lookup.index(dna)
            undiffused_dna_list.append(dna_lookup[(idx - steps) % 4])
        dna_encoded_channel = ''.join(undiffused_dna_list)

        # Decode back to pixel values
        decrypted_channel = np.array([
            dna_decode(dna_encoded_channel[i:i + 4])
            for i in range(0, len(dna_encoded_channel), 4)
        ]).reshape(M, N)

        decrypted_channels.append(decrypted_channel.astype(np.uint8))

    decrypted_image = cv2.merge(decrypted_channels)

    # Reverse Confusion
    logistic_sequence_r = logistic_map(params['a0'], params['mu_a'], M)
    logistic_sequence_c = logistic_map(params['b0'], params['mu_b'], N)

    # Invert permutation indices
    sorted_r_idx = np.argsort(logistic_sequence_r)
    sorted_c_idx = np.argsort(logistic_sequence_c)

    # Apply inverse permutation
    original_image = decrypted_image[np.argsort(sorted_r_idx), :]
    original_image = original_image[:, np.argsort(sorted_c_idx)]

    return original_image

@app.post("/encrypt")
async def encrypt_endpoint(
    file: UploadFile = File(...),
    a0: float = Form(0.1), b0: float = Form(0.2),
    mu_a: float = Form(3.99), mu_b: float = Form(3.99),
    z0: float = Form(0.1), q0: float = Form(0.2),
    wz: float = Form(5.0), wq: float = Form(5.0)
):
    # 1. Read Image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 2. Process
    params = {"a0": a0, "b0": b0, "mu_a": mu_a, "mu_b": mu_b, "z0": z0, "q0": q0, "wz": wz, "wq": wq}
    result = process_encrypt(image, params)

    # 3. Return Image
    _, encoded_img = cv2.imencode('.png', result)
    return StreamingResponse(io.BytesIO(encoded_img.tobytes()), media_type="image/png")

@app.post("/decrypt")
async def decrypt_endpoint(
    file: UploadFile = File(...),
    a0: float = Form(0.1), b0: float = Form(0.2),
    mu_a: float = Form(3.99), mu_b: float = Form(3.99),
    z0: float = Form(0.1), q0: float = Form(0.2),
    wz: float = Form(5.0), wq: float = Form(5.0)
):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    params = {"a0": a0, "b0": b0, "mu_a": mu_a, "mu_b": mu_b, "z0": z0, "q0": q0, "wz": wz, "wq": wq}
    result = process_decrypt(image, params)

    _, encoded_img = cv2.imencode('.png', result)
    return StreamingResponse(io.BytesIO(encoded_img.tobytes()), media_type="image/png")