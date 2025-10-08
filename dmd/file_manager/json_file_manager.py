import datetime
import gzip
import json
import os
import time


class TimesJSONFileManager:
    def __init__(self, dir_path: str, prefix: str = "result", suffix: str = "json", save_time_limit: int = 15):
        self.dir_path = dir_path
        self.prefix = prefix
        self.suffix = suffix
        self.save_time_limit = save_time_limit

    def _generate_filename(self):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        return f"{self.prefix}_{timestamp}.{self.suffix}"

    def save(self, data: dict):
        filename = self._generate_filename() + ".gz"
        path = os.path.join(self.dir_path, filename)
        with gzip.open(path, "wb") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8"))

    def _get_latest_file(self) -> str | None:
        files = [os.path.join(self.dir_path, f)
                 for f in os.listdir(self.dir_path)
                 if f.endswith(self.suffix) or f.endswith("gz") and f.startswith(self.prefix)]
        if not files:
            return None
        return max(files, key=os.path.getctime)

    def load(self):
        latest_file = self._get_latest_file()
        data = None
        if latest_file:
            with gzip.open(latest_file, "rb") as f:
                data = json.loads(f.read().decode("utf-8"))
        return data

    def delete_old_files(self):
        now = time.time()
        cutoff_time = now - self.save_time_limit * 24 * 60 * 60
        deleted_files = []
        for filename in os.listdir(self.dir_path):
            file_path = os.path.join(self.dir_path, filename)
            if os.path.isfile(file_path) and os.path.getctime(file_path) < cutoff_time:
                os.remove(file_path)
                deleted_files.append(filename)
        return deleted_files

    def run(self):
        """
        按顺序执行下面功能：
        1. 加载最新文件
        2. 删除超出时间界限的文件
        """
        data = self.load()
        self.delete_old_files()
        return data

