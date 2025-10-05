## HelixLock — Chaotic + DNA-inspired Image Encryption

HelixLock is a teaching/experimental project that encrypts color images using:

* **Permutation (confusion)** via the **logistic map**
* **Diffusion** via the **Chebyshev map**
* **DNA encoding** of pixel bytes (2-bit → nucleotide mapping)

---

## How it works (high level)

1. **Confusion (row/column shuffle):**
   Generate two chaotic sequences with the logistic map (parameters `a0, mu_a` for rows and `b0, mu_b` for columns), sort them, and use the sort indices to permute rows and columns.

2. **DNA diffusion:**
   Convert each pixel byte to a 4-letter DNA sequence using the 2-bit mapping:
   `00→A, 01→C, 10→G, 11→T`.
   A Chebyshev-driven sequence decides how many cyclic shifts to apply to each nucleotide, diffusing local structure.

3. **Decoding:**
   Turn DNA back into bytes, then merge the channels to get the encrypted image.
   Decryption reverses diffusion and then inverts the logistic permutations.

---

## Features

* Works on 8-bit color images (BGR via OpenCV).
* Deterministic encryption/decryption given the same parameters (the “key”).
* Simple, pure-Python + NumPy/OpenCV implementation.

---

## Requirements

* Python 3.8+
* NumPy
* OpenCV-Python

Install:

```bash
pip install -r requirements.txt
```

**requirements.txt**

```
numpy
opencv-python
```

----

## Quick start

### Encrypt

```
python encryption.py
```

Defaults (inside the script):

```python
encryption_parameters = {
    'a0': 0.4,
    'b0': 0.5,
    'mu_a': 3.99,
    'mu_b': 3.99,
    'z0': 0.6,   # currently unused in encryption
    'q0': 0.7,
    'wz': 2.0,   # currently unused in encryption
    'wq': 2.0
}
input_img_path = 'image.jpg'
output_img_path = 'encrypted_image.jpg'
```

### Decrypt

```
python decryption.py
```

Defaults (inside the script):

```python
a0, b0 = 0.4, 0.5
mu_a, mu_b = 3.99, 3.99
z0, q0 = 0.6, 0.7   # z0/wz computed but not used in the provided decryption logic
wz, wq = 2.0, 2.0
input:  encrypted_image.jpg
output: decrypted_image.jpg
```

> Use the **same parameters** for decryption that were used for encryption.

---

## Parameters (your “key material”)

| Name         | Role                               | Notes                                                   |
| ------------ | ---------------------------------- | ------------------------------------------------------- |
| `a0`, `mu_a` | Logistic map seed & control (rows) | `a0 ∈ (0,1)`, `mu_a` typically in (3.57, 4.0] for chaos |
| `b0`, `mu_b` | Logistic map seed & control (cols) | same domain as rows                                     |
| `q0`, `wq`   | Chebyshev seed & order (diffusion) | `q0 ∈ [-1,1]`, `wq > 1`                                 |
| `z0`, `wz`   | Reserved/extra Chebyshev stream    | Present but unused in current encrypt/decrypt flow      |

> Consider storing these in a small JSON “key file” and keep it with the ciphertext (or separately, depending on your threat model).

---

## API overview

### `encrypt_image(image, a0, b0, mu_a, mu_b, z0, q0, wz, wq) -> np.ndarray`

* **Input:** `image` as `H×W×3` `uint8` (BGR).
* **Output:** Encrypted image, same shape/dtype.
* **Steps:** Logistic permutation → DNA encode → Chebyshev diffusion → DNA decode.

### `decrypt_image(encrypted_image, a0, b0, mu_a, mu_b, z0, q0, wz, wq) -> np.ndarray`

* **Input:** Encrypted `H×W×3` `uint8`.
* **Output:** Decrypted (original) image.
* **Steps:** Reverse DNA diffusion → Invert logistic permutation.

---

## Notes & known quirks (from the provided code)

* **Unused params:** `z0`/`wz` are currently not used in `encrypt_image`. In `decrypt_image`, a `chebyshev_sequence_z` is computed but not used. You can either:

  * remove them from both scripts, **or**
  * extend diffusion to use both sequences (e.g., interleave two shift streams).
* **dtypes when merging:** In `decrypt_image`, ensure channels are `uint8` before `cv2.merge`. If you encounter type warnings, cast with `.astype(np.uint8)`.
* **Print message placement:** `decrypt_image` prints “saved to decrypted_image.jpg” inside the function, but saving happens in `__main__`. Consider moving the print or the `imwrite` so they’re consistent.
* **Performance:** `np.vectorize` is convenient but not especially fast. For large images, consider:

  * LUTs for DNA encode/decode (256-entry table),
  * operating on `view`ed bit arrays,
  * precomputing nucleotide shift maps.

---

## Troubleshooting

* **Colors look wrong or image corrupted:**
  Check that you used the **exact same parameters** for decryption. Also confirm saved arrays are `uint8`.
* **“Image not found” error:**
  Verify `input_image_path` is correct and the file exists.
* **Different size on decrypt:**
  Input and output sizes must match; do not resize between steps.

---

## Acknowledgements

Inspired by classic chaos-based permutation/diffusion schemes and DNA-mapping ideas in image encryption literature.
