from ete4.smartview import TreeStyle, NodeStyle, TreeLayout
from ete4.smartview.renderer.faces import RectFace, TextFace, AttrFace, CircleFace, SeqMotifFace, ScaleFace
from ete4.smartview.renderer.layouts import ncbi_taxonomy_layouts

from ete4 import Tree, PhyloTree
from ete4 import SeqGroup

from ete4.parser.newick import NewickError
#from ete4.smartview.renderer.layouts import seq_layouts

import csv 

tree = "./trees/phylotree.nw"
metadata = "./emmapper_annotations.tsv"
msa = "./fasta/tree.aln.faa"
fastafile = "./fasta/unaligned_NUP62.fasta"
layoutjson = "./ProteinDomainLayout.json"

def ete4_parse(newick):
    try:
        tree = PhyloTree(newick)        
    except NewickError:
        try:
            tree = PhyloTree(newick, format=1)            
        except NewickError:
            tree = PhyloTree(newick, format=1, quoted_node_names=True)

    # Correct 0-dist trees
    has_dist = False
    for n in tree.traverse(): 
        if n.dist > 0: 
            has_dist = True
            break
    if not has_dist: 
        for n in tree.iter_descendants(): 
            n.dist = 1

    return tree

def parse_emapper(metadata):
    metatable = []
    tsv_file = open(metadata)
    read_tsv = csv.DictReader(tsv_file, delimiter="\t")

    for row in read_tsv:
        metatable.append(row)
    tsv_file.close()
    return metatable, read_tsv.fieldnames

t = ete4_parse(tree)

# add props to leaf
annotations, columns = parse_emapper(metadata)

#['#query', 'seed_ortholog', 'evalue', 'score', 'eggNOG_OGs', 'max_annot_lvl', 'COG_category', 'Description', \
# 'Preferred_name', 'GOs', 'EC', 'KEGG_ko', 'KEGG_Pathway', 'KEGG_Module', 'KEGG_Reaction', 'KEGG_rclass', \
# 'BRITE', 'KEGG_TC', 'CAZy', 'BiGG_Reaction', 'PFAMs']
for annotation in annotations:
    gene_name = next(iter(annotation.items()))[1] #gene name must be on first column
    #print(list(annotation.values())[0])
    try:
        target_node = t.search_nodes(name=gene_name)[0]
        for _ in range(1, len(columns)):
            
            if columns[_] == 'seed_ortholog': # only for emapper annotations
                taxid, gene = annotation[columns[_]].split('.', 1)
                target_node.add_prop('taxid', taxid)
                target_node.add_prop('gene', gene)
            target_node.add_prop(columns[_], annotation[columns[_]])
    except:
        pass

def parse_fasta(fastafile):
    fasta_dict = {}
    with open(fastafile,'r') as f:
        head = ''
        seq = ''
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if seq != '':
                    fasta_dict[head] = seq
                    seq = ''
                    head = line[1:]
                else:
                    head = line[1:]
            else:
                seq += line
    fasta_dict[head] = seq

    return fasta_dict

import json
def parse_json(jsonfile):
    with open(layoutjson) as json_file:
        data = json.load(json_file)
    return data

PROTEIN_NAME_TO_SEQ = parse_fasta(fastafile)
#PROTEIN_TO_DOMAINS = parse_json(layoutjson)
# taxa annotation
t.annotate_ncbi_taxa('taxid')
t.write(outfile="annotated_tree.nw", properties=[], format=1)

# add layouts to leaf
def get_level(node, level=1):
    if node.is_root():
        return level
    else:
        return get_level(node.up, level + 1)

def get_layout_SeedOrtholog(tree):
    column = 1
    rect_width = 15
    def layout_fn(node):
        
        if node.props.get('sci_name'):
            lca = node.props.get('sci_name')
            color = node.props.get('sci_name_color', 'lightgray')
            
            level = get_level(node, level=1)
            lca_face = RectFace(15, float('inf'), 
                    color = color, 
                    text = lca,
                    fgcolor = "white",
                    padding_x = 1, padding_y = 1)
            lca_face.rotate_text = True
            node.add_face(lca_face, position='aligned', column=level)
            node.add_face(lca_face, position='aligned', column=level,
                collapsed_only=True)
            #print(node)

    #layout_fn.__name__ = 'Last common ancestor'
    #layout_fn.contains_aligned_face = True
    return layout_fn

def get_layout_lca_rects():
    def layout_new(node):
        nstyle = NodeStyle()
        if not node.up:
            # Modify the aspect of the root node
            nstyle["fgcolor"] = "red" # yellow
            nstyle["size"] = 15
            node.set_style(nstyle)
        else:
            # Creates an independent node style for each node, which is
            # initialized with a red foreground color.
            nstyle = NodeStyle()
            nstyle["fgcolor"] = "green" # blue
            nstyle["size"] = 5
            node.set_style(nstyle)
    return layout_new

def get_layout_lca_rects2(tree):


    def layout_fn(node):
       
        if node.props.get('lca_node_name'):
            lca = node.props.get('lca_node_name')
            color = node.props.get('_Lca_color')
            
            level = get_level(node)
            lca_face = RectFace(15, float('inf'), 
                    color = color , 
                    text = lca,
                    fgcolor = "white",
                    padding_x = 1, padding_y = 1)
            lca_face.rotate_text = True
            node.add_face(lca_face, position='aligned', column=level)
            node.add_face(lca_face, position='aligned', column=level,
                collapsed_only=True)

    

    layout_fn.__name__ = 'Last common ancestor'
    layout_fn.contains_aligned_face = True
    return layout_fn

def get_layout_gnames():
    def layout_new(node):
        nstyle = NodeStyle()
        if node.is_leaf():
            # Modify the aspect of the root node
            #nstyle["fgcolor"] = "green" # yellow
            nstyle["size"] = 5
            node.set_style(nstyle)
            node.add_face(TextFace(f'{node.props.get("Preferred_name")}',
                        color='skyblue'), 
                        column=0, position='aligned')
    return layout_new



class LayoutAlignment(TreeLayout):
    def __init__(self, alignment=None, format='seq', width=700, height=15,
            column=0, range=None, summarize_inner_nodes=False):
        super().__init__('Alignment')
        self.alignment = SeqGroup(alignment) if alignment else None
        self.width = width
        self.height = height
        self.column = column
        self.aligned_faces = True
        self.format = format

        self.length = len(next(self.alignment.iter_entries())[1]) if self.alignment else None
        self.scale_range = range or (0, self.length)
        self.summarize_inner_nodes = summarize_inner_nodes

    def set_tree_style(self, tree_style):
        if self.length:
            face = ScaleFace(width=self.width, scale_range=self.scale_range, padding_y=10)
            tree_style.aligned_panel_header.add_face(face, column=0)
            tree_style.collapse_size = 1

    def _get_seq(self, node):
        if self.alignment:
            return self.alignment.get_seq(node.name)
        return node.props.get("seq", None)

    def get_seq(self, node):
        if node.is_leaf():
            return self._get_seq(node)

        if self.summarize_inner_nodes:
            # TODO: summarize inner node's seq
            return None
        else:
            first_leaf = next(node.iter_leaves())
            return self._get_seq(first_leaf)
    
    def set_node_style(self, node):
        seq = self.get_seq(node)

        if seq:
            seqFace = SeqMotifFace(seq, seq_format=self.format, bgcolor='grey',
                    width=self.width, height=self.height)
            node.add_face(seqFace, column=self.column, position='aligned',
                    collapsed_only=(not node.is_leaf())) 

def get_layout_pfam():
    def layout(node):
        if node.is_leaf():
            if node.name in PROTEIN_TO_DOMAINS:
                seq = PROTEIN_NAME_TO_SEQ[node.name]
                protDomains = PROTEIN_TO_DOMAINS[node.name]
                seqFace = SeqMotifFace(seq, protDomains)
                node.add_face(seqFace, position="aligned", column=0)
    return layout

def get_svg(ete_server_ur, treeid, w=370, h=170):

    r = requests.get('%s/trees/%s/size' %(ete_server_url, treeid), verify=False)
    tree_size = r.json()
    zx = w / tree_size["width"]
    zy = h / tree_size["height"]
    r = requests.get('%s/trees/%s/draw?zx=%s&zy=%s&drawer=Rect' %(ete_server_url, treeid, zx, zy), verify=False)
    graph_items = r.json()

    svg = svgwrite.Drawing(size=(w, h))
    for item in graph_items:
        if item[0] == 'line':
            (x0, y0), (x1, y1) = item[1], item[2]
            svg.add(svg.line((x0*zx, y0*zy), (x1*zx, y1*zy), stroke=svgwrite.rgb(10, 10, 16, '%')))
    return svg.tostring()

from ete4.smartview.renderer.layouts import seq_layouts
from multiprocessing import Process
import time
from selenium_test import browser_driver
import requests

t.draw(tree_name="example", layouts=[
    TreeLayout("gname", ns=get_layout_gnames(), aligned_faces = True),
])

# def run(t):
#     t.explore(tree_name="example", layouts=[
#         TreeLayout("taxa", ns=get_layout_SeedOrtholog(t), aligned_faces = True),
#         #TreeLayout("lca", ns=get_layout_lca_rects(), aligned_faces = True),
#         TreeLayout("gname", ns=get_layout_gnames(), aligned_faces = True),
#         #TreeLayout("seq", ts=seq_layouts, aligned_faces = True),
#         #TreeLayout("lca", ns=get_layout_lca_rects2(t), aligned_faces = True),
#         #TreeLayout("seq", ns=get_layout_pfam(), aligned_faces = True),
#         #LayoutAlignment()
#         ]
#         )
#     return

# def job2():
#     url = "http://127.0.0.1:5000/static/gui.html?tree=example"

#     def end_flask():
#         requests.get('http://localhost:5000/shutdown')
#         return

#     browser_driver(url)

#     time.sleep(0.5)

#     #print("quit")
#     #end_flask()
#     return

# p = Process(target=run, args=(t,))
# p.start()

# p2 = Process(target=job2)
# p2.start()
# time.sleep(3)
# p.terminate()
# p.join()


#import os
# pid = os.fork()
# if pid == 0:
#     print("start")
#     # t.explore(tree_name="example", layouts=[
#     #     TreeLayout("taxa", ns=get_layout_SeedOrtholog(t), aligned_faces = True),
#     #     #TreeLayout("lca", ns=get_layout_lca_rects(), aligned_faces = True),
#     #     TreeLayout("gname", ns=get_layout_gnames(), aligned_faces = True),
#     #     #TreeLayout("seq", ts=seq_layouts, aligned_faces = True),
#     #     #TreeLayout("lca", ns=get_layout_lca_rects2(t), aligned_faces = True),
#     #     #TreeLayout("seq", ns=get_layout_pfam(), aligned_faces = True),
#     #     #LayoutAlignment()
#     #     ], 
#     #     render_template=True
#     #     )
#     # import requests
#     # requests.get('http://127.0.0.1:5000/shutdown')
# else:
#     # import requests
#     # requests.get('http://127.0.0.1:5000/shutdown')
#     # t.explore(tree_name="example", layouts=[
#     #     TreeLayout("taxa", ns=get_layout_SeedOrtholog(t), aligned_faces = True),
#     #     #TreeLayout("lca", ns=get_layout_lca_rects(), aligned_faces = True),
#     #     TreeLayout("gname", ns=get_layout_gnames(), aligned_faces = True),
#     #     #TreeLayout("seq", ts=seq_layouts, aligned_faces = True),
#     #     #TreeLayout("lca", ns=get_layout_lca_rects2(t), aligned_faces = True),
#     #     #TreeLayout("seq", ns=get_layout_pfam(), aligned_faces = True),
#     #     #LayoutAlignment()
#     #     ], 
#     #     render_template=True
#     #     )
#     print("shut it down!")
    

# print('after server')
# from ete4.smartview import TreeStyle, NodeStyle, TreeLayout
# ts = TreeStyle()
# ts.show_leaf_name = True

# t.render(file_name="example.png")