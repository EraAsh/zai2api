import base64
import json
import time
import hashlib
import random
import string
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

class DarkKnightGenerator:
    """
    生成 zai.is 所需的 x-zai-darkknight 请求头
    基于逆向工程的逻辑实现
    """
    
    def __init__(self):
        self.backend = default_backend()
        
    def generate(self):
        """生成完整的 darkknight 字符串"""
        try:
            # 1. 生成 EC 密钥对 (P-256)
            private_key = ec.generate_private_key(ec.SECP256R1(), self.backend)
            public_key = private_key.public_key()
            
            # 2. 导出公钥为 JWK 格式
            # 注意：cryptography 库不直接支持导出 JWK，我们需要手动构建
            public_numbers = public_key.public_numbers()
            x = self._int_to_base64url(public_numbers.x)
            y = self._int_to_base64url(public_numbers.y)
            
            jwk = {
                "kty": "EC",
                "crv": "P-256",
                "x": x,
                "y": y
            }
            
            # 3. 生成指纹 (Fingerprint)
            # 模拟浏览器指纹
            fingerprint = self._generate_fingerprint()
            
            # 4. 构建 payload
            payload = {
                "v": 1,
                "ts": int(time.time() * 1000),
                "nonce": self._generate_nonce(),
                "fp": fingerprint,
                "pk": jwk
            }
            
            # 5. 序列化并签名
            # 这里简化处理，实际可能需要对 payload 进行签名
            # 但根据观察，darkknight 主要是 base64 编码的 JSON
            
            json_str = json.dumps(payload, separators=(',', ':'))
            
            # 6. 对 payload 进行签名 (使用私钥)
            # 实际逻辑中，客户端使用私钥对 payload 的哈希进行签名
            signature = private_key.sign(
                json_str.encode(),
                ec.ECDSA(hashes.SHA256())
            )
            
            # 7. 将签名添加到 payload (或者作为单独部分)
            # 根据逆向 JS，最终结构可能包含签名
            # 这里我们模拟一个结构
            final_data = {
                **payload,
                "sig": self._base64url_encode(signature)
            }
            
            final_json = json.dumps(final_data, separators=(',', ':'))
            return self._base64url_encode(final_json.encode())
            
        except Exception as e:
            print(f"Error generating darkknight: {e}")
            return None

    def _int_to_base64url(self, val):
        """将整数转换为 base64url 编码的字符串"""
        # P-256 是 256 位，即 32 字节
        byte_len = (val.bit_length() + 7) // 8
        bytes_val = val.to_bytes(byte_len, 'big')
        return self._base64url_encode(bytes_val)

    def _base64url_encode(self, data):
        """Base64URL 编码"""
        if isinstance(data, str):
            data = data.encode()
        encoded = base64.urlsafe_b64encode(data).decode('utf-8')
        return encoded.rstrip('=')

    def _generate_nonce(self, length=16):
        """生成随机 nonce"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def _generate_fingerprint(self):
        """生成模拟的浏览器指纹"""
        # 这是一个简化的指纹，实际指纹更复杂
        components = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "en-US",
            "24", # color depth
            "1920x1080", # resolution
            "-480", # timezone offset
            "Win32", # platform
            "true", # cookies enabled
            "PDF Viewer,Chrome PDF Viewer,Chromium PDF Viewer,Microsoft Edge PDF Viewer,WebKit built-in PDF" # plugins
        ]
        fingerprint_str = "|".join(components)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()

# 简单的测试
if __name__ == "__main__":
    from cryptography.hazmat.primitives import hashes
    generator = DarkKnightGenerator()
    dk = generator.generate()
    print(f"Generated DarkKnight: {dk}")