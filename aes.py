from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from hashlib import sha256
import os

def encrypt_file(filename, key):
    hashed_key = sha256(key.encode()).digest()

    with open(filename, 'rb') as f:
        plaintext = f.read()

    cipher = AES.new(hashed_key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

    enc_filename = f"{filename}.enc"
    with open(enc_filename, 'wb') as f:
        f.write(cipher.iv + ciphertext)

    os.remove(filename)
    print(f"Encrypted: {enc_filename} (Original file deleted)")

    return enc_filename


def decrypt_file(enc_filename, key):
    hashed_key = sha256(key.encode()).digest()

    with open(enc_filename, 'rb') as f:
        iv = f.read(16)  
        ciphertext = f.read()

    try:
        cipher = AES.new(hashed_key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

        original_filename = enc_filename.replace('.enc', '')

        with open(original_filename, 'wb') as f:
            f.write(decrypted)

        print(f"Decrypted successfully: {original_filename}")
        return original_filename

    except ValueError as e:
        print("Decryption failed: Incorrect key or corrupted file!")
        return None


if __name__ == "__main__":
    key = "my_secret_key"

    encrypted_file = encrypt_file("OIP.jpg", key)

    decrypted_file = decrypt_file(encrypted_file, key)
    print("\nOriginal file restored:", decrypted_file)
