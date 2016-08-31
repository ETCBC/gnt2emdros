import xml.etree.ElementTree as ET
import glob
import os
import collections

'''

SBLGNT loops through the files in the source directory and stores the data structures into 'nodes,' a dict.
Only the XML tags 'Sentence' and 'Node' are stored.
Only these are stored since the 3 others (Sentences, Trees, Tree) are not relevant for mql.
Variable 'nodes' stores the tag as a key and all of its descendants as the 'nodeId' number.
Sentences are stored first as they encompass all other linguistic objects in SBLGNT and will serve as the starting point
...to generate monad numbers.

'''


class SBLGNT:
    def __init__(self, setup):
        # assembles the XML files from the source directory to be converted
        self.input_files = [x for x in glob.glob("{}/*".format(setup.input_dir)) if os.path.splitext(x)[1] == '.xml'] # !! CHECK THE ORDER HERE !!
        self.nodes = collections.OrderedDict()
        self.node_descendants = collections.OrderedDict()
        self.sentences = collections.OrderedDict()

        for file in self.input_files:
            print('Extracting from '+file+'...')
            self.tree_climber(file, 'Node', self.nodes, self.node_descendants)
            self.tree_climber(file, 'Sentence', self.sentences, '')

        # TODO: IS THERE A CLEANER WAY TO DO THIS??
        # Adjustment to avoid error in mql,
        # because the attrib 'Type' is a used word in the mql language, the code alters the attrib to 'typ'
        for n in self.nodes:
            if 'Type' in self.nodes[n]:
                temp = self.nodes[n]['Type']
                del self.nodes[n]['Type']
                self.nodes[n]['typ'] = temp

    # climbs the XML tree and extracts the attributes and descendants for a given tag (see above, 'Sentences', 'Node')
    def tree_climber(self, file, tag, dict1, dict2):
        tree = ET.parse(file)
        root = tree.getroot()
        for node in root.iter(tag):
            if node.attrib and tag != 'Sentence':
                dict1[node.attrib['nodeId']] = node.attrib
                dict2[node.attrib['nodeId']] = list(node_descendant.attrib['nodeId'] for node_descendant in node.findall('.//') if node_descendant.attrib)
            elif tag == 'Sentence':
                sentence_node = list(node_descendant.attrib['nodeId'] for node_descendant in node.findall('.//') if node_descendant.attrib)[0]
                dict1[sentence_node] = node.attrib['ID']
