import os
from tabulate import tabulate
from dmd.config import Config
from dmd.logger import get_logger
logger = get_logger(__name__)

class DirectoryUsageTracker(object):
    def __init__(self, config: Config):
        self.dir_path = config.RC.dir_path
        self.top_n = config.RC.top_n
        self.min_size = config.RC.min_size
        self.target_folders = None
        logger.info(f"配置加载完成 - 扫描根目录: {self.dir_path}")
        logger.info(f"配置加载完成 - 展示Top N: {self.top_n}, min_size: {self.min_size}字节")
        self.new_folders_tree = self._get_new_folders_tree()
        self.root_node = list(self.new_folders_tree.keys())[0]

    def _get_new_folders_tree(self):
        new_folders_tree = self.__class__.get_folders_tree(self.dir_path)
        self.__class__.get_folders_tree_size(new_folders_tree)
        return new_folders_tree

    def get_change_of_folders(self, old_folders_tree: dict):
        # 根据old_tree_folder, new_tree_folder创建一个中间变化树
        change_folders_tree = __class__.get_change_folders_tree(old_folders_tree, self.new_folders_tree, self.root_node)
        self.target_folders = __class__.get_top_n_memory_consuming_folders(self.root_node, change_folders_tree, self.top_n, self.min_size)
        return self.target_folders

    def __str__(self):
        table_data = [["文件夹路径", "增加大小(byte)"]]
        for folder in self.target_folders:
            for key, value in folder.items():
                # 转换数字为带千位分隔符的字符串
                if isinstance(value, (int, float)):
                    value_str = f"{value:,}"
                else:
                    value_str = str(value)
                table_data.append([key, value_str])

        return tabulate(table_data, headers="firstrow", tablefmt="grid", stralign="left", numalign="right")

    @staticmethod
    def get_folders_tree(root_path: str):
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
                    tree[root_path]["children"].append(__class__.get_folders_tree(full_path))
                elif os.path.isfile(full_path):  # 需要进行判断，用于跳过无权限访问的文件
                    tree[root_path]["children"].append({full_path: {"size": None, "type": "file"}})
            except PermissionError:
                logger.warning(f"无法访问 {full_path} , 权限不够，已经跳过 ")
        return tree

    @staticmethod
    def get_folders_tree_size(tree_folders: dict):
        """
        计算get_tree_folders得到的文件夹的树形结构表示的文件或者文件夹大小
        :param tree_folders: 文件夹的树形结构表示
        :return:
        """
        for key, item in tree_folders.items():
            if item["type"] == "file":
                try:
                    item["size"] = os.path.getsize(key)
                except FileNotFoundError:
                    item["size"] = 0
                    logger.warning(f"File disappeared during scan and was skipped: {key}")
                return item["size"]
        total_size = 0
        for key in tree_folders.keys():
            for child in tree_folders[key]["children"]:
                total_size += __class__.get_folders_tree_size(child)
            tree_folders[key]["size"] = total_size
        return total_size

    @staticmethod
    def get_change_folders_tree(old_tree_folder, new_tree_folder, root_node):
        change_tree_folder = {}
        change_size = new_tree_folder[root_node]["size"] - old_tree_folder[root_node]["size"]
        change_tree_folder[root_node] = {"node_type": '+', "change_size": change_size,
                                         "type": new_tree_folder[root_node]["type"], "children": []}

        if new_tree_folder[root_node]["type"] == "file" and old_tree_folder[root_node]["type"] == "file":
            return change_tree_folder

        # 处理孩子节点
        # 对old_tree_folder
        old_children = set()
        for child in old_tree_folder[root_node]["children"]:
            old_children.add(list(child.keys())[0])

        new_children = set()
        for child in new_tree_folder[root_node]["children"]:
            new_children.add(list(child.keys())[0])

        intersection = old_children & new_children
        difference_new_old = new_children - intersection
        difference_old_new = old_children - intersection
        for item in intersection:
            # change_size = new_tree_folder[root_node]["children"][item]["size"] - old_tree_folder[root_node]["children"][item]["size"]
            # change_tree_folder[root_node]["children"].append({item: {"node_type": '+', "change_size": change_size, "children": []}})
            new_index = None
            for i, d in enumerate(new_tree_folder[root_node]['children']):
                if item in d:
                    new_index = i
                    break
            old_index = None
            for i, d in enumerate(old_tree_folder[root_node]['children']):
                if item in d:
                    old_index = i
                    break
            # 递归找到更加详细信息
            child_node = __class__.get_change_folders_tree(old_tree_folder[root_node]['children'][old_index],
                                                new_tree_folder[root_node]['children'][new_index], item)
            # change_tree_folder[root_node]["children"][item]["children"].append(child_node)
            change_tree_folder[root_node]["children"].append(child_node)

        for item in difference_new_old:
            index = None
            for i, d in enumerate(new_tree_folder[root_node]['children']):
                if item in d:
                    index = i
                    break
            change_size = new_tree_folder[root_node]["children"][index][item]["size"]
            change_tree_folder[root_node]["children"].append({item: {"node_type": '+', "change_size": change_size,
                                                                     "type":
                                                                         new_tree_folder[root_node]["children"][index][
                                                                             item]["type"], "children": []}})

        for item in difference_old_new:
            index = None
            for i, d in enumerate(old_tree_folder[root_node]['children']):
                if item in d:
                    index = i
                    break
            change_size = old_tree_folder[root_node]["children"][index][item]["size"]
            change_tree_folder[root_node]["children"].append({item: {"node_type": '-', "change_size": change_size,
                                                                     "type":
                                                                         old_tree_folder[root_node]["children"][index][
                                                                             item]["type"], "children": []}})
        return change_tree_folder

    @staticmethod
    def get_top_n_memory_consuming_folders(root_node: str, tree_folder: dict, top_n: int, min_size: int) -> list:
        """
        从构造文件树(tree_folder)中挑选top_n个内存增加>min_size的文件夹。如果一对父子文件夹，子文件夹满足挑选条件，
        那么在计算父文件夹时需要先减去子文件夹的增加量，再判断是否>min_size。
        :param root_node: 文件路径，也是字典的键
        :param tree_folder: 文件树的字典表示
        :param top_n: 挑选内存增加最多的top_n个文件夹
        :param min_size: 文件夹内存增加量 > min_size才会被挑选，单位为字节
        :return:
        """
        folders = []
        change_size = tree_folder[root_node]['change_size']
        for child in tree_folder[root_node]['children']:
            child_node = list(child.keys())[0]
            child_change_size = child[child_node]['change_size']
            child_node_type = child[child_node]['node_type']
            child_type = child[child_node]['type']
            if child_node_type == '-':
                continue
            else:
                if child_change_size >= min_size and child_type == 'folder':
                    change_size -= child_change_size
                    child_folders = __class__.get_top_n_memory_consuming_folders(child_node, child, top_n, min_size)
                    for child_folder in child_folders:
                        folders.append(child_folder)
                else:
                    continue

        if change_size >= min_size:
            folders.append({root_node: change_size})
        target_folders = sorted(folders, key=lambda x: list(x.values())[0], reverse=True)[:top_n]
        return target_folders
