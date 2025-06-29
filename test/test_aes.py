import time
import matplotlib.pyplot as plt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

plaintext = b"23374/PL2.3/KM/20220|Laita Zidan|2141762100"
iterations = 1000

key_sizes = {
    'AES-128': 16,
    'AES-192': 24,
    'AES-256': 32
}

encrypt_times = []
decrypt_times = []

for key_name, key_length in key_sizes.items():
    key = get_random_bytes(key_length)
    iv = get_random_bytes(16)

    encrypt_time = 0
    decrypt_time = 0

    for _ in range(iterations):
        # Enkripsi
        start_enc = time.time()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
        encrypt_time += (time.time() - start_enc)

        # Dekripsi
        start_dec = time.time()
        cipher_dec = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher_dec.decrypt(ciphertext), AES.block_size)
        decrypt_time += (time.time() - start_dec)

        # Validasi
        assert decrypted == plaintext, "Dekripsi gagal!"

    avg_enc = encrypt_time / iterations
    avg_dec = decrypt_time / iterations

    encrypt_times.append(avg_enc)
    decrypt_times.append(avg_dec)

    print(f"{key_name} - Rata-rata Enkripsi: {avg_enc:.10f}s, Dekripsi: {avg_dec:.10f}s")

# Buat Grafik
x_labels = list(key_sizes.keys())
x_pos = range(len(x_labels))

plt.figure(figsize=(10, 6))
plt.bar([x - 0.15 for x in x_pos], encrypt_times, width=0.3, label='Enkripsi')
plt.bar([x + 0.15 for x in x_pos], decrypt_times, width=0.3, label='Dekripsi')
plt.xticks(x_pos, x_labels)
plt.ylabel('Waktu Rata-rata (detik)')
plt.title(f'Perbandingan Kecepatan AES - {iterations} Iterasi')
plt.legend()
plt.tight_layout()
plt.show()