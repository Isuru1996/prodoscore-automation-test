from automation_lib.api import BaseApiClient

from ..api_responses import (
    ProdoscoreDecryptResponse,
    ProdoscoreEncryptResponse,
    ProdoscoreHashResponse,
    ProdoscoreHealthResponse,
)


class ProdoscoreCryptoClient(BaseApiClient):
    def __init__(self, base_url="http://localhost:8080", default_headers=None):
        super().__init__(base_url, default_headers)

    def health(self):
        return ProdoscoreHealthResponse(self.get("/health"))

    def encrypt(self, plain_text):
        return ProdoscoreEncryptResponse(
            self.post("/enc", json={"plain_text": plain_text})
        )

    def decrypt(self, cipher_text):
        return ProdoscoreDecryptResponse(
            self.post("/dec", json={"cipher": cipher_text})
        )

    def hash(self, text):
        return ProdoscoreHashResponse(self.post("/hash", json={"text": text}))
