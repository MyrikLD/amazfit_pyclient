from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes


def encrypt_aes(value, secret_key):
    cipher = Cipher(algorithms.AES(secret_key), modes.ECB())
    encryptor = cipher.encryptor()
    ct = encryptor.update(value) + encryptor.finalize()
    return ct


def decrypt_aes(value, secret_key):
    cipher = Cipher(algorithms.AES(secret_key), modes.ECB())
    decryptor = cipher.decryptor()
    pt = decryptor.update(value) + decryptor.finalize()
    return pt
