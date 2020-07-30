from __future__ import annotations
from _collections_abc import Iterable, Sized
from enum import Enum
from uuid import uuid4
from time import perf_counter
import os
from shutil import copy2
from shutil import copyfileobj
import gzip
import xml.etree.ElementTree as ET
import ntpath


class AvailableCollections(Enum):
    __order__ = 'list dict set tuple'
    list = list
    dict = dict
    set = set
    tuple = tuple


def is_available_collection(obj):
    return type(obj) in [type(i.value()) for i in AvailableCollections]


def is_iterable(obj: object):
    return isinstance(obj, Iterable)


def is_sized(obj: object):
    return isinstance(obj, Sized)


class Node:
    def __init__(self, ):
        self.id = uuid4()

    @staticmethod
    def from_dict(d, key: object = None) -> Node:
        assert type(d) == dict
        root = Collection(dict, True, [], [])
        for key, val in d:
            root.add_child(Node.from_any(val, key=key))
        return root

    @staticmethod
    def from_any(obj, key: object = None) -> Node:
        if is_available_collection(obj):
            if type(obj) == dict:
                return Node.from_dict(obj, key=key)

        else:
            raise NotImplementedError

    @staticmethod
    def is_value(item):
        return not is_available_collection(item)


class Collection(Node):
    def __init__(self, key: str = None, children: list = list):
        super().__init__()
        self.key = key
        self.children = children

    def get_amount_children(self):
        return len(self.children)

    def add_child(self, child: Node):
        self.children.append(child)


class AlsNode(Collection):

    def __init__(self, key: str = None, attrib: dict = dict, children: list = list):
        super().__init__(key, children)
        self.key = key
        self.attrib = attrib
        self.str_depth = 2

    def __str__(self):
        return self.recursive_str(0, self.str_depth)

    def recursive_str(self, depth=1, max_depth=4):
        info = "Key: {}, Attrib: {}".format(self.key, self.attrib)
        if depth <= max_depth:
            for c in self.children:
                info += "\n" + (depth * "-") + c.recursive_str(depth=depth+1, max_depth=max_depth)
        return info

    @staticmethod
    def get(base_node: AlsNode, node_path: list):
        assert len(node_path) >= 1
        cur_path = node_path[0]
        if base_node.key == cur_path:

            if len(node_path) == 1:
                return base_node
            else:
                for c in base_node.children:
                    res = AlsNode.get(c, node_path[1:])
                    if res is not None:
                        return res

    @staticmethod
    def recursive_find_first(base_node: AlsNode, key: str):
        full_path = [base_node.key]
        if base_node.key == key:
            return base_node, full_path
        else:
            n = None
            for c in base_node.children:
                n, partial_path = AlsNode.recursive_find_first(c, key)
                if n is not None:
                    full_path = full_path + partial_path
                    return n, full_path
        return n, full_path

    @staticmethod
    def from_file(full_path) -> AlsNode:
        tree = AlsNode.etree_from_als_file(full_path)
        root = tree.getroot()
        return AlsNode.recursive_scan(root)

    @staticmethod
    def recursive_scan(etree_node):
        new_children = [AlsNode(
            key=child.tag,
            attrib=child.attrib,
            children=[AlsNode.recursive_scan(c) for c in child])
        for child in etree_node
        ]
        new_root = AlsNode(key=etree_node.tag, attrib=etree_node.attrib, children=new_children)
        return new_root

    @staticmethod
    def etree_from_als_file(full_path):
        assert full_path[-3:] == 'als'
        path, filename = split_path_and_filename(full_path)
        filename = filename[:-4]
        gz_file = os.path.join(path, filename + ".gz")
        copy2(full_path, gz_file)

        #   Extracting file
        xml_file = os.path.join(path, filename + ".xml")  # new destination of xml file

        with gzip.open(gz_file, 'rb') as f_in:
            with open(xml_file, 'wb') as f_out:
                copyfileobj(f_in, f_out)

        os.remove(gz_file)  # Deleting gz
        #os.remove(xml_file)  # Deleting xml
        return ET.parse(xml_file)

    def write_deprecated(self, tree=None):
        if tree is None:
            tree = self.tree

        file_name = self.adress + self.filename + "_re.xml"
        tree.write(file_name, encoding='utf-8', xml_declaration=True)  # writing xml file to adress

        # Compressing .xml file

        with open(file_name, 'rb') as f_in:
            with gzip.open(self.adress + self.filename + ".gz", 'wb') as f_out:
                copyfileobj(f_in, f_out)

        # Renaming .gz file

        copy2(self.adress + self.filename + ".gz", self.adress + self.filename + "_re.als")
        os.remove(self.adress + self.filename + ".gz")
        # os.remove(self.adress + self.filename + "_re.xml")

    def to_list(self, root):
        list = []
        for child in root:
            list.append(child)  # .append(self.to_list(child))
            list.extend(self.to_list(child))

        return list


#SuperNode = Node(None)


def absolute_file_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def split_path_and_filename(path):
    head, tail = ntpath.split(path)
    return head, tail


def measure_time():
    length = 10000

    for i in range(length):
        start = perf_counter()
        elapsed = perf_counter()-start
        print("Avg time for Fib(500) is: {}:10.7".format(elapsed/100))


if __name__ == "__main__":
    path = "D:\\AbletonArchive\\Jonas Mastering Project\\Jonas Mastering.als"
    node = AlsNode.from_file(path)
    node_, path = node.recursive_find_first(base_node=node, key='Tracks')
    print(str(node))
    node = node.get(node, path)
