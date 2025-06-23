#!/bin/bash

# ===============================
# OPENSSL TEST SCRIPT – BLOCKCHAIN VERIFIKASI SERTIFIKAT
# ===============================

# Cari direktori utama proyek
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

# Path absolut ke file kunci
PRIVATE_KEY_PATH="$PROJECT_ROOT/backend/keys/private_key.pem"
PUBLIC_KEY_PATH="$PROJECT_ROOT/backend/keys/public_key.pem"

# AES Key dan IV
AES_KEY_HEX=$(echo -n "MySecretAESKey1234567890123456" | xxd -p)  # 32 byte
IV_HEX="00000000000000000000000000000000"

# File sementara
INPUT_FILE="$SCRIPT_DIR/input.txt"
SIGNATURE_FILE="$SCRIPT_DIR/signature.bin"
ENCRYPTED_FILE="$SCRIPT_DIR/data.enc"
DECRYPTED_FILE="$SCRIPT_DIR/data_decrypted.txt"

# Input data langsung
INPUT_STRING="23374/PL2.3/KM/20220|Laita Zidan|2141762100"
echo -n "$INPUT_STRING" > "$INPUT_FILE"

echo "=============================="
echo "🔐 PENGUJIAN OPENSSL – KRIPTOGRAFI SISTEM"
echo "=============================="

# [1] Cek panjang dan isi RSA Private Key
echo "🧾 [1] Validasi RSA Private Key:"
openssl rsa -in "$PRIVATE_KEY_PATH" -text -noout | grep "Private-Key"

# [2] Tanda tangan RSA
echo "✍️ [2] Menandatangani input string..."
openssl dgst -md5 -sign "$PRIVATE_KEY_PATH" -out "$SIGNATURE_FILE" "$INPUT_FILE"

# [3] Verifikasi signature
echo "✅ [3] Verifikasi tanda tangan:"
openssl dgst -md5 -verify "$PUBLIC_KEY_PATH" -signature "$SIGNATURE_FILE" "$INPUT_FILE"

# [4] Enkripsi AES
echo "🔐 [4] Enkripsi AES-256:"
openssl enc -aes-256-cbc -salt -in "$INPUT_FILE" -out "$ENCRYPTED_FILE" -K "$AES_KEY_HEX" -iv "$IV_HEX"
echo "📦 Enkripsi selesai: $ENCRYPTED_FILE"

# [5] Dekripsi AES
echo "🔓 [5] Dekripsi AES-256:"
openssl enc -aes-256-cbc -d -in "$ENCRYPTED_FILE" -out "$DECRYPTED_FILE" -K "$AES_KEY_HEX" -iv "$IV_HEX"
echo "📄 Hasil dekripsi:"
cat "$DECRYPTED_FILE"

# [6] Validasi hasil dekripsi
echo "🔍 [6] Validasi hasil dekripsi..."
if cmp -s "$INPUT_FILE" "$DECRYPTED_FILE"; then
  echo "✅ Dekripsi berhasil: data sesuai"
else
  echo "❌ Dekripsi gagal: data tidak cocok"
fi

echo "=============================="
echo "🧪 UJI KRIPTOGRAFI SELESAI"
echo "=============================="