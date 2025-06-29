import hashlib
import time
import matplotlib.pyplot as plt

# Data yang akan di-hash
data = "23374/PL2.3/KM/2022|Laita Zidan|2141762100".encode('utf-8')
iterations = 10000  # Jumlah iterasi uji

# Definisi fungsi hashing
def md5_hash(data):
    return hashlib.md5(data).hexdigest()

def sha1_hash(data):
    return hashlib.sha1(data).hexdigest()

def sha256_hash(data):
    return hashlib.sha256(data).hexdigest()

# Benchmark fungsi
def benchmark_hash(name, hash_func):
    total_time = 0
    for _ in range(iterations):
        start = time.time()
        hash_func(data)
        total_time += (time.time() - start)
    avg_time = total_time / iterations
    return avg_time

# Jalankan benchmark
results = {}
results['MD5'] = benchmark_hash('MD5', md5_hash)
results['SHA-1'] = benchmark_hash('SHA-1', sha1_hash)
results['SHA-256'] = benchmark_hash('SHA-256', sha256_hash)

# Tampilkan hasil rata-rata
print("\n=== Hasil Rata-rata Waktu Hashing ===")
for algo, avg_time in results.items():
    print(f"{algo}: {avg_time:.10f} detik per hash")

# Visualisasi grafik
plt.figure(figsize=(8, 6))
plt.bar(results.keys(), results.values(), color=['blue', 'green', 'red'])
plt.ylabel('Waktu Rata-rata per Hash (detik)')
plt.title(f'Perbandingan Kecepatan Hashing ({iterations} Iterasi)')
plt.tight_layout()
plt.show()