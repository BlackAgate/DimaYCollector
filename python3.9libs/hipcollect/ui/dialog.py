import os
import shutil

from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSplitter
import hou
import importlib

from hipcollect.ui import listview, listviewparms
from hipcollect.ui.utility import get_human_readable
from hipcollect.ui import button
from hipcollect import saver
from hipcollect import files_parser
from hipcollect import hip_parser

class SubmitDialog(QDialog):
    def __init__(self,parms,parent=None):
        super(SubmitDialog, self).__init__(parent)
        
        importlib.reload(listview)
        importlib.reload(listviewparms)
        importlib.reload(saver)
        
        importlib.reload(button)
        
        self.tree_list_parms = listviewparms.CustomListViewParms(parms)   
        self.tree_list_parms.root_dialog = self
        self.tree_list_parms.itemClicked.connect(self.on_item_tree_list_parms_clicked)
        self.tree_list = listview.CustomListView()
        self.tree_list_parms.tree_list = self.tree_list        
        self.tree_list.itemClicked.connect(self.on_item_tree_list_clicked)
 
        self.setWindowTitle("DimaY Houdini Collector")
        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        self.submit_button = button.CollectFolderButton("Collect to folder...")
        self.submit_button.clicked.connect(lambda: self.save_files(mode="folder"))
        self.submit_button_hip = button.CollectToHipButton("Collect to current HIP project...")
        self.submit_button_hip.clicked.connect(lambda: self.save_files(mode="hip"))
        self.size = QLabel(get_human_readable(self.tree_list.total_size))
        self.resize(1800, 1000)
        
        splitter = QSplitter(self)
        splitter.addWidget(self.tree_list)
        splitter.addWidget(self.tree_list_parms)
        layout.addWidget(splitter, stretch=10)
        h_layout.addWidget(self.submit_button, stretch=10)
        h_layout.addWidget(self.submit_button_hip, stretch=10)
        h_layout.addWidget(QLabel("Total size:"), stretch=1)
        self.size = QLabel(get_human_readable(self.tree_list.total_size))
        h_layout.addWidget(self.size, stretch=1)
        layout.addLayout(h_layout, stretch=.1)
        self.attention = QLabel("ATTENTION: collector will only copy references within the scene FRAME RANGE. Adjust it if necessary.")
        layout.addWidget(self.attention, stretch=.1)
        
        self.description = QLabel("<a href='https://www.behance.net/yarkov' style='color: white;'>Dima Yarkov 2024</a>")
        self.description.setOpenExternalLinks(True)
        layout.addWidget(self.description, stretch=.1)
        self.setLayout(layout)
        
    def process_and_create_second_tree(self):
        results = []
        for i in range(self.tree_list_parms.topLevelItemCount()):
            item = self.tree_list_parms.topLevelItem(i)
            parm = item.data(4,0)
            refs = self.extract_refs(parm)
            results.append((item, refs))
        self.create_tree_list(results)
 
    def extract_refs(self,parm): #extract refs frame by frame here. Replace custom_data with parm
        start_frame = int(hou.playbar.frameRange()[0])
        end_frame = int(hou.playbar.frameRange()[1])
        refs = set()
        for frame in range(start_frame, end_frame + 1, 1):
            ref, valid = hip_parser.ref_convert(parm,frame)
            if valid:
                refs.add(ref)
        return (refs)
        
    def create_tree_list(self,results):
        self.tree_list.results = results
        self.tree_list.tree_list_parms = self.tree_list_parms
        self.tree_list.root_dialog = self
        self.tree_list.addPaths(results, self.tree_list_parms)

    def update_total_size(self):
        self.size.setText(get_human_readable(self.tree_list.total_size))
        self.size.update()
 
    def on_item_tree_list_clicked(self,item):
        indexes = item.data(4,0)
        if indexes is not None:
            index_of_first_parent_parm = indexes[0]
            item_parm_from_index = self.tree_list_parms.itemFromIndex(index_of_first_parent_parm)
            parm_stored_ref_indexes = item_parm_from_index.data(4,0)
            for index in parm_stored_ref_indexes: #select all linked refs
                child = self.tree_list.itemFromIndex(index)
                child.setSelected(1)
            self.tree_list_parms.clearSelection()
            for index in indexes: #select all linked parms
                parm_item = self.tree_list_parms.itemFromIndex(index)
                parm_item.setSelected(1)
                self.tree_list_parms.scrollToItem(parm_item)
        
    def on_item_tree_list_parms_clicked(self,item):
        indexes = item.data(4,0)
        index_of_first_child_ref = indexes[0]
        item_ref_from_index = self.tree_list_parms.itemFromIndex(index_of_first_child_ref)
        ref_stored_parm_indexes = item_ref_from_index.data(4,0)
        for index in ref_stored_parm_indexes:
            item_from_index = self.tree_list_parms.itemFromIndex(index)
            item_from_index.setSelected(1)

        self.tree_list.clearSelection()
        for index in indexes:
            list_item = self.tree_list.itemFromIndex(index)
            list_item.setSelected(1)
            self.tree_list.scrollToItem(list_item)

    def button_handle(self, tree_list_parms):
        button.ToolButtonParm.remove_parm(tree_list_parms,self.tree_list)

    def save_files(self,mode="folder"):
        target_dir = None
        if mode == "folder":
            target_dir = hou.ui.selectFile(file_type=hou.fileType.Directory)
        else:
            response = hou.ui.displayMessage("Collect local files to a current HIP project and fix associated paths?", buttons=("OK", "Cancel"))
            if response == 0:
                target_dir = os.path.dirname(hou.hipFile.path())
        if target_dir:
            target_dir = hou.text.expandString(target_dir).lower()
            with hou.undos.group("Change nodes paths"):
                with hou.InterruptableOperation("Saving scene dependencies...", open_interrupt_dialog=True) as oper:
                    oper.updateProgress(0)
                    for i, parm in enumerate(self.tree_list_parms.files):                        
                        oper.updateProgress(i/len(self.tree_list_parms.files))
                        importlib.reload(files_parser)
                        if "filecache" in parm.node().type().nameComponents()[2]:
                            files_parser.filecache_parse(parm,target_dir,mode)
                        else: #all other nodes except filecache
                            files_parser.allfiles_parse(parm,target_dir,mode)           
            if mode == "folder":
                hou.hipFile.save()
                path = hou.hipFile.path()
                shutil.copy(path, target_dir)
                hou.undos.performUndo()
            hou.ui.displayMessage("Saved successfully!")