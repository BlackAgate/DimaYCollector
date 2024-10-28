import hou
from PySide2.QtWidgets import QTreeWidget, QHeaderView, QTreeWidgetItem
from hipcollect.ui import button
import importlib

class CustomListViewParms(QTreeWidget):
    def __init__(self, parms, parent=None):
        super(CustomListViewParms, self).__init__(parent)

        self.files = set()
        self.error_files = set()
        self.total_size = 0
        self.root_dialog = None
        self.tree_list = None
        self.processed_ref_indexes = set()
        self.resize(1500,500)
        self.setHeaderLabels(["Node", "Original Ref", " ", " ", "Parm","List Ref Index", " "])
        self.setColumnHidden(4,1)
        self.setColumnHidden(5,1)
        
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 600)
        self.setColumnWidth(2, 15)
        self.setColumnWidth(3, 15)
        self.setColumnWidth(6, 15)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0,QHeaderView.Stretch)

    def addPaths(self, parms): #for QTreeWidget
        importlib.reload(button)
        refs = set()
        for parm in parms:
            node = parm.path()
            link = parm.eval()
            try:
                ref = parm.unexpandedString()
            except:
                ref = parm.eval()
            new_child = QTreeWidgetItem([node,ref])
            self.files.add(parm)
            new_child.setData(4, 0, parm)
            prev = self.addTopLevelItem(new_child)
            rem_button = button.ToolButtonParm(new_child, self.files, parm, link, self.root_dialog, self.tree_list, self, icon="remove")
            rem_button.clicked.connect(rem_button.remove_parm)
            self.setItemWidget(new_child, 6, rem_button)
            show_button = button.ToolButtonParm(new_child, self.files, parm, link, self.root_dialog, self.tree_list, self, icon="toobject")
            show_button.clicked.connect(show_button.show_parm)
            self.setItemWidget(new_child, 3, show_button)
            show_button = button.ToolButtonParm(new_child, self.files, parm, link, self.root_dialog, self.tree_list, self, icon="open")
            show_button.clicked.connect(show_button.show_item)
            self.setItemWidget(new_child, 2, show_button)
            
        self.resizeColumnToContents(0)
        self.sortByColumn(0)
        self.setSortingEnabled(1)