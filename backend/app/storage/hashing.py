import hashlib


def calculate_sha256(file_content: bytes) -> str:
    return hashlib.sha256(file_content).hexdigest()
