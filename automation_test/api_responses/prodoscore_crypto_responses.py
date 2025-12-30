from automation_lib.api.base_response import BaseApiResponse


class HealthResponse(BaseApiResponse):
    @property
    def service(self):
        return self.data.get("Service") if self.data else None


class EncryptResponse(BaseApiResponse):
    @property
    def cipher(self):
        return self.data.get("cipher") if self.data else None


class DecryptResponse(BaseApiResponse):
    @property
    def plain_text(self):
        return self.data.get("plain_text") if self.data else None


class HashResponse(BaseApiResponse):
    @property
    def hash(self):
        return self.data.get("hash") if self.data else None
