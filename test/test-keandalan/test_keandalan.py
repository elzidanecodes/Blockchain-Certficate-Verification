import time
import requests
import matplotlib.pyplot as plt

def test_keandalan(zip_file_path, server_url="http://localhost:5000/verify_certificate_zip"):
    """
    Menguji keandalan endpoint verifikasi batch dengan file ZIP.
    Menampilkan statistik dan grafik durasi per file.
    """

    # Mulai stopwatch
    with open(zip_file_path, 'rb') as zip_file:
        files = {'file': zip_file}
        print("🚀 Mulai pengujian...")
        start = time.time()
        response = requests.post(server_url, files=files)
        end = time.time()

    total_time = end - start
    print(f"⏱️ Durasi Total Request: {total_time:.2f} detik")

    if response.status_code != 200:
        print("❌ Gagal verifikasi")
        print(f"Status: {response.status_code}")
        print("Respon:", response.text)
        return

    data = response.json()

    # Statistik
    jumlah = data.get("jumlah_total", 0)
    berhasil = data.get("verified_count", 0)
    durasi_backend = data.get("durasi_total", "?")
    rata_rata = data.get("rata_rata_per_file", "?")

    print("✅ Verifikasi selesai.")
    print(f"📦 Total file: {jumlah}")
    print(f"✔️ Berhasil diverifikasi: {berhasil}")
    print(f"🕒 Durasi dari backend: {durasi_backend}")
    print(f"📉 Rata-rata backend per file: {rata_rata}")
    print(f"🧭 Durasi total dari client: {total_time:.2f} detik")

    # Ekstrak durasi simulasi (jika backend tidak kirim detail tiap file)
    hasil = data.get("hasil", [])
    durations = []
    for i, h in enumerate(hasil):
        # Simulasi saja: semua sukses dianggap ~0.3 detik, gagal ~0.1
        if h.get("status") == "success":
            durations.append(0.3)
        else:
            durations.append(0.1)

    # Plot chart
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, len(durations) + 1), durations, marker='o')
    plt.title("Durasi Verifikasi per Sertifikat (Simulasi)")
    plt.xlabel("Nomor Sertifikat ke-")
    plt.ylabel("Durasi (detik)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    test_keandalan("all_certificates(1).zip")