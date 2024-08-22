from io import StringIO
import tarfile
import logging
import enumerate
from PyQt6 import QtWidgets
logger=logging.getLogger(__name__)

def parse_config_file(filename)->dict:
    result={}
    current_category=None
    with open(filename) as f:
        for line in f:
            line=line.strip()
            if line.startswith('[') and line.endswith(']'):
                current_category=line[1:-1]
                result[current_category]={}
            else:
                key,value=line.split('=',1)
                result[current_category][key.strip()]=value.strip()
    return result

def parse_string(content)->dict:
    result={}
    current_category=None
    lines=content.splitlines()
    for line in lines:
        line=line.strip()
        if line.startswith('[') and line.endswith(']'):
            current_category=line[1:-1]
            result[current_category]={}
        else:
            try:
                key,value=line.split('=',1)
                result[current_category][key.strip()]=value.strip()
            except Exception as e:
                logger.error(f"Error parsing line: {line}")
                logger.error(e)
    return result


def compare_diff_dict_2comparedto1(file1_data:dict, file2_data:dict):
    result = {}
    logger.info("start compare diff by dict")
    # Compare sections and keys
    for section in set(file1_data.keys()).union(file2_data.keys()):
        result[section] = {}
        if section in file1_data and section in file2_data:
            for key in set(file1_data[section].keys()).union(file2_data[section].keys()):
                if key in file1_data[section] and key in file2_data[section]:
                    if file1_data[section][key] == file2_data[section][key]:
                        pass
                        #result[section][key] = (enumerate.DiffType.SAME, file1_data[section][key])
                    else:
                        result[section][key] = (enumerate.DiffType.MODIFIED, file1_data[section][key], file2_data[section][key])
                elif key in file1_data[section]:
                    result[section][key] = (enumerate.DiffType.REMOVED, file1_data[section][key])
                elif key in file2_data[section]:
                    result[section][key] = (enumerate.DiffType.ADDED, file2_data[section][key])
        elif section in file1_data:
            for key in file1_data[section]:
                result[section][key] = (enumerate.DiffType.REMOVED, file1_data[section][key])
        elif section in file2_data:
            for key in file2_data[section]:
                result[section][key] = (enumerate.DiffType.ADDED, file2_data[section][key])
    #logger.debug(result)
    return result


def load_textfile_to_string(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def load_textfile_to_list(file_path):
    with open(file_path, 'r') as file:
        content = file.readlines()
    return content


def load_tgz_to_string(tgz_path):
    with tarfile.open(tgz_path, "r:gz") as tar:
        member = tar.getmembers()[0]  # 获取第一个文件
        file = tar.extractfile(member)
        content = file.read().decode('utf-8')
    return content
        
        
def save_string_to_tgz(string, tgz_path):
    with tarfile.open(tgz_path, "w:gz") as tar:
        file = tarfile.TarInfo(name="file.txt")
        file.size = len(string)
        tar.addfile(file, fileobj=StringIO(string))
    return tgz_path

def save_string_to_textfile(string, file_path):
    with open(file_path, 'w') as file:
        file.write(string)
    return file_path

def load_tgz_to_list(tgz_path):
    list=[]
    with tarfile.open(tgz_path, "r:gz") as tar:
        member = tar.getmembers()[0]
        file = tar.extractfile(member)
        if file is not None:
            while True:
                chunk = file.read(1024)  # 每次读取1024字节
                if not chunk:
                    break
                list.append(chunk.decode('utf-8'))
    return list


