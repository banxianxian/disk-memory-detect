import psutil
import os
from psutil._common import bytes2human
from dmd.logger import get_logger
logger = get_logger(__name__)
def get_disk_name():
    """
    获得电脑磁盘的名字
    """
    return [part.device for part in psutil.disk_partitions(all=False)]


def get_disk_usage(disk_name: str=None):
    """
    获取全部磁盘或者某个磁盘的使用情况
    :param disk_name:
    :return:(dict)
    """
    disk_usage = {}
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or not part.fstype:
                continue

        usage = psutil.disk_usage(part.mountpoint)
        disk_usage[part.device] = {
            'total': bytes2human(usage.total),
            'used': bytes2human(usage.used),
            'free': bytes2human(usage.free),
            'percent': usage.percent,
        }
    if disk_name:
        try:
            return {disk_name: disk_usage[disk_name]}
        except KeyError:
            raise ValueError(f"Disk {disk_name} not found. Available disks: {list(disk_usage.keys())}")
    return disk_usage


def get_folders_size(root_path: str):
    """
    获取root_path以及其路径下所有文件夹大小
    :param root_path: 根路径
    :return:(dict) {文件名1：文件大小1，文件名2：文件大小2…………}
    """
    folders_size = {}
    for dir_path, dir_names, file_names in reversed(list(os.walk(root_path))):
        total_size = 0
        # dir_path目录下的文件大小记录
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                pass

        # dir_path目录下的文件夹大小记录
        for dir_name in dir_names:
            subdir = os.path.join(dir_path, dir_name)
            total_size += folders_size.get(subdir, 0)

        # 构造树形结构(字典)
        folders_size[dir_path] = total_size
    return folders_size


def get_tree_folders(root_path: str):
    """
    将文件夹的层级关系用树(字典)表示
    :param root_path: 根路径
    :return: {父文件名：{'size': None, 'type': folder 或者 file， 'children': [子文件1， 子文件2] 或者 空, }
    """
    tree = {root_path: {"size": None, "type": "folder", "children": []}}
    for entry in os.listdir(root_path):
        full_path = os.path.join(root_path, entry)
        try:
            if os.path.isdir(full_path):
                tree[root_path]["children"].append(get_tree_folders(full_path))
            elif os.path.isfile(full_path):         # 需要进行判断，用于跳过无权限访问的文件
                tree[root_path]["children"].append({full_path: {"size": None, "type": "file"}})
        except PermissionError:
            logger.warning(f"无法访问 {full_path} , 权限不够，已经跳过 ")
    return tree


def get_tree_folders_size(tree_folders: dict):
    """
    计算get_tree_folders得到的文件夹的树形结构表示的文件或者文件夹大小
    :param tree_folders: 文件夹的树形结构表示
    :return:
    """
    for key, item in tree_folders.items():
        if item["type"] == "file":
            item["size"] = os.path.getsize(key)
            return item["size"]
    total_size = 0
    for key in tree_folders.keys():
        for child in tree_folders[key]["children"]:
            total_size += get_tree_folders_size(child)
        tree_folders[key]["size"] = total_size
    return total_size



# from save_tools import save_dict_to_json, load_dict_from_json
# path = r"F:\F_Disk\projects\langchain_learn"
# tree_folders = get_tree_folders(path)
# print(tree_folders)
# tree_folders_size = get_tree_folders_size(tree_folders)
# print(tree_folders_size)
# print(tree_folders)
# save_dict_to_json(tree_folders, "file_tree2.json")





