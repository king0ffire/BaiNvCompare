import tarfile
import logging
import os

logger = logging.getLogger(__name__)


def parse_config_file(filename) -> dict:
    result = {}
    current_category = None
    result[current_category] = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                current_category = line[1:-1]
                result[current_category] = {}
            else:
                key, value = line.split("=", 1)
                result[current_category][key.strip()] = value.strip()
    return result


def load_textfile_to_string(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content


def load_textfile_to_list(file_path):
    with open(file_path, "r") as file:
        content = file.readlines()
    return content


def load_tgz_to_string(tgz_path):
    with tarfile.open(tgz_path, "r:gz") as tar:
        member = tar.getmembers()[0]  # 获取第一个文件
        file = tar.extractfile(member)
        content = file.read().decode("utf-8")  # type: ignore raise会被上面接住
    return member.name, content


def save_string_to_tgz(string, tgz_path, temp_filename):
    with tarfile.open(tgz_path, "w:gz") as new_tar:
        with open(temp_filename, "w") as temp_file:
            temp_file.write(string)
        new_tar.add(temp_filename)
    os.remove(temp_filename)
    return tgz_path


def save_string_to_textfile(string, file_path):
    with open(file_path, "w") as file:
        file.write(string)
    return file_path


def load_tgz_to_list(tgz_path):
    list = []
    with tarfile.open(tgz_path, "r:gz") as tar:
        member = tar.getmembers()[0]
        file = tar.extractfile(member)
        if file is not None:
            while True:
                chunk = file.read(1024)  # 每次读取1024字节
                if not chunk:
                    break
                list.append(chunk.decode("utf-8"))
    return list
