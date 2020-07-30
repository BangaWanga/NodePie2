import os
from shutil import copy2
from shutil import copyfileobj
import gzip
import xml.etree.ElementTree as ET


class ALS_Node(Node):

    def __init__(self):
        self.tree = None
        self.als_root = None #Type: xml Tree
        self.als_list = None
        self.temp = []
        self.adress = None #folder of .file
        self.filename = None
        self.xml_data = None



    def from_file(self, filepath):
        #   Renaming .als file
        gz_file = path + "/" + filename + ".gz"
        copy2(filepath, gz_file)

        #   Extracting file
        xml_file = path + "/" + filename + ".xml" # new destination of xml file

        with gzip.open(gz_file, 'rb') as f_in:
            with open(xml_file, 'wb') as f_out:
                copyfileobj(f_in, f_out)
                self.xml_data = f_out

        os.remove(gz_file)        # Deleting gz
        tree = ET.parse(xml_file)
        os.remove(xml_file)        # Deleting xml

        self.tree = tree

        self.als_root = tree.getroot()


    def write_deprecated(self, tree=None):
        if tree is None:
            tree = self.tree

        file_name = self.adress + self.filename + "_re.xml"
        tree.write(file_name, encoding='utf-8', xml_declaration=True)   # writing xml file to adress

        #Compressing .xml file

        with open(file_name, 'rb') as f_in:
            with gzip.open(self.adress+ self.filename +".gz", 'wb') as f_out:
                copyfileobj(f_in, f_out)

        #Renaming .gz file

        copy2(self.adress + self.filename + ".gz", self.adress + self.filename + "_re.als")
        os.remove(self.adress + self.filename + ".gz")
        #os.remove(self.adress + self.filename + "_re.xml")

    def to_list(self, root):
        list = []
        for child in root:
            list.append(child) # .append(self.to_list(child))
            list.extend(self.to_list(child))

        return list







if __name__=="__main__":
    als_r = ALS_Reader()
    als_r.scan("/windows/Users/Nicolas Schilling/Ableton Live/Testing/test.als")
    als_r.add_midi_track(pos = 2)
    als_r.write()