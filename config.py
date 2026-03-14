import json
import os

class Config:
    DEFAULT_CONFIG = {
        'force_mode': 'auto',  # auto, gpu, disk
        'gpu_index': 0,
        'disk_path': '/'
    }

    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.DEFAULT_CONFIG, **json.load(f)}
            except Exception as e:
                print(f"配置文件加载失败: {e}, 使用默认配置")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def get(self, key, default=None):
        return self.config.get(key, default)
