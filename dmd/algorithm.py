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
                child_folders = get_top_n_memory_consuming_folders(child_node, child, top_n, min_size)
                for child_folder in child_folders:
                    folders.append(child_folder)
            else:
                continue

    if change_size >= min_size:
        folders.append({root_node: change_size})
    target_folders = sorted(folders, key=lambda x: list(x.values())[0], reverse=True)[:top_n]
    return target_folders


def get_change_tree_folder(old_folder_tree, new_folder_tree, root_node):
    change_tree_folder = {}
    change_size = new_folder_tree[root_node]["size"] - old_folder_tree[root_node]["size"]
    change_tree_folder[root_node] = {"node_type": '+', "change_size": change_size,"type": new_folder_tree[root_node]["type"] , "children": []}

    if new_folder_tree[root_node]["type"] == "file" and old_folder_tree[root_node]["type"] == "file":
        return  change_tree_folder

    # 处理孩子节点
    # 对old_tree_folder
    old_children = set()
    for child in old_folder_tree[root_node]["children"]:
        old_children.add(list(child.keys())[0])

    new_children = set()
    for child in new_folder_tree[root_node]["children"]:
        new_children.add(list(child.keys())[0])

    intersection = old_children & new_children
    difference_new_old = new_children - intersection
    difference_old_new = old_children - intersection
    for item in intersection:
        #change_size = new_tree_folder[root_node]["children"][item]["size"] - old_tree_folder[root_node]["children"][item]["size"]
        #change_tree_folder[root_node]["children"].append({item: {"node_type": '+', "change_size": change_size, "children": []}})
        new_index = None
        for i, d in enumerate(new_folder_tree[root_node]['children']):
            if item in d:
                new_index = i
                break
        old_index = None
        for i, d in enumerate(old_folder_tree[root_node]['children']):
            if item in d:
                old_index = i
                break
        # 递归找到更加详细信息
        child_node = get_change_tree_folder(old_folder_tree[root_node]['children'][old_index], new_folder_tree[root_node]['children'][new_index], item)
        #change_tree_folder[root_node]["children"][item]["children"].append(child_node)
        change_tree_folder[root_node]["children"].append(child_node)

    for item in difference_new_old:
        index = None
        for i, d in enumerate(new_folder_tree[root_node]['children']):
            if item in d:
                index = i
                break
        change_size = new_folder_tree[root_node]["children"][index][item]["size"]
        change_tree_folder[root_node]["children"].append({item: {"node_type": '+', "change_size": change_size, "type": new_folder_tree[root_node]["children"][index][item]["type"], "children": []}})

    for item in difference_old_new:
        index = None
        for i, d in enumerate(old_folder_tree[root_node]['children']):
            if item in d:
                index = i
                break
        change_size = old_folder_tree[root_node]["children"][index][item]["size"]
        change_tree_folder[root_node]["children"].append({item: {"node_type": '-', "change_size": change_size,"type": old_folder_tree[root_node]["children"][index][item]["type"], "children": []}})
    return change_tree_folder


def dick_change_tracker(old_tree_folder, new_tree_folder):
    # 根据old_tree_folder, new_tree_folder创建一个中间变化树
    root_node = list(old_tree_folder.keys())[0]
    change_tree_folder = get_change_tree_folder(old_tree_folder, new_tree_folder, root_node)
    return change_tree_folder