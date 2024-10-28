import glob
import os, hou
import importlib

from PySide2.QtWidgets import QTreeWidget, QHeaderView, QTreeWidgetItem

from hipcollect.ui import button
from hipcollect.ui.utility import get_human_readable

class CustomListView(QTreeWidget):
    def __init__(self, parent=None):
        super(CustomListView, self).__init__(parent)
        self.files = set()
        self.error_files = set()
        self.total_size = 0
        self.results = None
        self.tree_list_parms = None
        self.root_dialog = None
        self.processed_parm_indexes = set()
        self.tree_list_parms = None
        self.resize(1500,500)
        self.setHeaderLabels(["Local Files", "Size", " ", " ", "Index", "Ref"])
        self.setColumnHidden(4,1)
        self.setColumnHidden(5,1)
        self.setColumnWidth(0, 800)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 15)
        self.setColumnWidth(3, 15)
        self.resizeColumnToContents(0)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0,QHeaderView.Stretch)

    def addPaths(self, results, tree_list_parms):
        with hou.InterruptableOperation("Building list...",open_interrupt_dialog=True) as oper:
            oper.updateProgress(0)
            processed_refs_tuple = []
            for i, (original_item, refs) in enumerate(results):
                oper.updateProgress(i/len(results))                
                index_of_original_item = tree_list_parms.indexFromItem(original_item)
                ref_indexes = []
                for ref in refs:
                    for tup in processed_refs_tuple: #checks if ref has already been processed
                        if ref in tup[0][0]:
                            tup_item = tup[0][1]
                            stored_parm_indexes = tup_item.data(4,0)
                            stored_parm_indexes.append(index_of_original_item)
                            tup_item.setData(4,0,stored_parm_indexes) #storing all associated parameters in the ref item
                            ref_indexes.append(self.indexFromItem(tup_item)) 
                            original_item.setData(5,0,ref_indexes) #storing duplicate associated ref in the current found parameter
                            break
                    else: #if ref hasn't been processed creates a new item
                        disk = os.path.splitdrive(ref)[0]
                        prev = None
                        for i in range(self.topLevelItemCount()):
                            if disk == self.topLevelItem(i).text(0):
                                prev = self.topLevelItem(i)
                        if not prev:
                            prev = QTreeWidgetItem([disk])
                            self.addTopLevelItem(prev)
                        path = ref.split("/")[1:]
                        counter = 0
                        for item in path:
                            flag = 0
                            for i in range(prev.childCount()):
                                if item == prev.child(i).text(0):
                                    prev = prev.child(i)
                                    flag = 1
                                    break
                            if not flag:
                                if counter != len(path) - 1:
                                    new_child = QTreeWidgetItem([item])
                                    folder_path = os.path.join(ref.split(item)[0], item)
                                    prev.addChild(new_child)
                                    prev = new_child
                                else:
                                    if "<udim>" in ref:
                                        for udim in glob.glob(ref.replace("<udim>", "*")):
                                            leaf_processed_tuple = self.addLeaf(udim, prev, original_item, index_of_original_item, ref_indexes)
                                            processed_refs_tuple.append(leaf_processed_tuple)
                                    else:
                                        leaf_processed_tuple = self.addLeaf(ref, prev, original_item, index_of_original_item, ref_indexes)
                                        processed_refs_tuple.append(leaf_processed_tuple)
                            counter += 1
            # self.root_dialog.update_total_size()
            self.expandAll() #be carefull about moving this. Getting things expanded in a wrong place of a code may lead to a massive slowdown            
        
    def addLeaf(self, ref, prev, original_item, index_of_original_item, ref_indexes):
        importlib.reload(button)
        try:
            size = os.path.getsize(ref)
        except:
            self.error_files.add(ref)
            return
        self.total_size += size
        size = get_human_readable(size)
        
        new_child = QTreeWidgetItem([os.path.basename(ref), size])
        prev.addChild(new_child)
        processed_refs_tuple = [(ref,new_child)]
        ref_indexes.append(self.indexFromItem(new_child))
        original_item.setData(5,0,ref_indexes) #storing all associated references in the original parameter item
        new_child.setData(4,0,[index_of_original_item]) #storing single associated parameter in the ref item if there are no more
        new_child.setData(5,0,ref)

        self.files.add(ref)
        new_child.setSelected(True)
        rem_button = button.ToolButton(new_child, self.files, ref, self.root_dialog, self, self.tree_list_parms)
        rem_button.clicked.connect(rem_button.remove_item)
        self.setItemWidget(new_child, 3, rem_button)
        show_button = button.ToolButton(new_child, self.files, ref, self.root_dialog, self, self.tree_list_parms, icon="show")
        show_button.clicked.connect(show_button.show_item)
        self.setItemWidget(new_child, 2, show_button)
        return processed_refs_tuple