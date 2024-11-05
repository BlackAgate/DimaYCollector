from PySide2.QtWidgets import QToolButton, QStyle, QApplication, QPushButton, QToolTip
from PySide2.QtGui import QPalette, QColor, QIcon
import os, hou
import webbrowser
import importlib

from hipcollect.ui import utility

class CollectFolderButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
    def enterEvent(self, event):
        tooltip_palette = QPalette()
        tooltip_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))  # Background color
        tooltip_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))  # Text color
        QToolTip.showText(self.mapToGlobal(self.rect().center()), """Collects all dependencies into the specified folder
Builds assosiated paths from $HIP if nesessary
Copies updated HIP-scene to the same folder
Current scene does not change.
        """)
        QToolTip.setPalette(tooltip_palette)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)
        
class CollectToHipButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
    def enterEvent(self, event):
        tooltip_palette = QPalette()
        tooltip_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))  # Background color
        tooltip_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))  # Text color
        QToolTip.showText(self.mapToGlobal(self.rect().center()), """Copies all dependencies to the current HIP folder
Changes assosiated paths from $HIP if nesessary
You can undo paths changes if desired (one undo operation)
        """)
        QToolTip.setPalette(tooltip_palette)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)        

class ToolButton(QToolButton):
    def __init__(self, item, files, link, root, tree_list, tree_list_parms, parent=None, icon="remove"):
        super(ToolButton, self).__init__(parent)
        self.item = item
        self.files = files
        self.link = link
        self.root = root
        self.tree_list = tree_list
        self.tree_list_parms = tree_list_parms
        self.processed_parm_indexes = tree_list.processed_parm_indexes
        if icon == "remove":
            icon = QApplication.style().standardIcon(QStyle.SP_TitleBarCloseButton)
        else:
            icon = QApplication.style().standardIcon(QStyle.SP_DirOpenIcon)
        self.setIcon(icon)

    def remove_item(self):
        importlib.reload(utility)
        child = self.item
        indexes = child.data(4,0) #each reference stores a list of parameters pointing on it, here we read this list
        if indexes is not None:
            childs,parm_items = utility.return_connected_refs(self.tree_list,self.tree_list_parms,child,indexes)
            for child in childs:
                link = child.data(5,0) #get stored ref data
                self.files.remove(link)
                size = os.path.getsize(link)
                self.tree_list.total_size -= size
                self.root.update_total_size()
                parent = child.parent()
                while parent:
                    parent.removeChild(child)
                    if not parent.childCount():
                        child = parent
                        parent = child.parent()
                    else:
                        parent = None
            for parm in parm_items:
                index_of_top_level = self.tree_list_parms.indexOfTopLevelItem(parm)
                self.tree_list_parms.takeTopLevelItem(index_of_top_level)

    def show_item(self):
        webbrowser.open(os.path.dirname(self.link))
               
class ToolButtonParm(QToolButton):
    def __init__(self, item, files, link, ref, root, tree_list, tree_list_parms, parent=None, icon="remove"):
        super(ToolButtonParm, self).__init__(parent)
        self.item = item
        self.files = files
        self.link = link
        self.ref = ref
        self.root = root
        self.tree_list_parms = tree_list_parms
        self.tree_list = tree_list
        self.processed_ref_indexes = tree_list_parms.processed_ref_indexes
        if icon == "remove":
            icon = QApplication.style().standardIcon(QStyle.SP_TitleBarCloseButton)
        elif icon == "open":
            icon = QApplication.style().standardIcon(QStyle.SP_DirOpenIcon)
        else:
            icon = QIcon()
            icon.addPixmap(hou.qt.createIcon("jump").pixmap(32,32),QIcon.Normal, QIcon.On)
            # icon = QApplication.style().standardIcon(QStyle.SP_MediaPlay)
        self.setIcon(icon)
   
    def remove_parm(self):
        importlib.reload(utility)
        item = self.item
        parm_items,childs = utility.return_connected_parms(self.tree_list,self.tree_list_parms,item)
        for parm in parm_items:
            index_of_top_level = self.tree_list_parms.indexOfTopLevelItem(parm)
            self.tree_list_parms.takeTopLevelItem(index_of_top_level)
        for child in childs: #performing deletion
            link = child.data(5,0) #get stored ref data
            self.tree_list.files.remove(link)
            size = os.path.getsize(link)
            self.tree_list.total_size -= size
            self.root.update_total_size()
            parent = child.parent()
            while parent:
                parent.removeChild(child)
                if not parent.childCount():
                    child = parent
                    parent = child.parent()
                else:
                    parent = None

    def show_parm(self):
        parm = self.link
        node = parm.node()
        hou.clearAllSelected()
        node.setSelected(True)
        
    def show_item(self):
        webbrowser.open(os.path.dirname(self.ref))        