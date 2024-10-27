from PySide2.QtWidgets import QToolButton, QStyle, QApplication, QPushButton, QToolTip
from PySide2.QtGui import QPalette, QColor, QIcon
import os, hou
import webbrowser

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
        child = self.item
        self.remove_all_linked_refs(child)
        self.remove_all_linked_parms(child)
   
    def remove_all_linked_refs(self,item):
        index_of_first_parent_parm = item.data(4,0)[0]
        item_parm_from_index = self.tree_list_parms.itemFromIndex(index_of_first_parent_parm)
        parm_stored_ref_indexes = item_parm_from_index.data(4,0)
        childs = set()
        for index in parm_stored_ref_indexes:
            childs.add(self.tree_list.itemFromIndex(index))
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
        
    def remove_all_linked_parms(self,item):
        processed_parm_indexes = self.processed_parm_indexes
        indexes = item.data(4,0)
        for index in indexes:
            index_string = str(index)
            position = index_string.find(" at ")
            index_string = index_string[:position]
            if index_string not in processed_parm_indexes:
                item_from_index = self.tree_list_parms.itemFromIndex(index)
                self.processed_parm_indexes.add(index_string)
                index_of_top_level = self.tree_list_parms.indexOfTopLevelItem(item_from_index)
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
        item = self.item
        self.remove_all_linked_parms(item)
        self.remove_all_linked_refs(item)
        
    def remove_all_linked_parms(self,item):
        index_of_first_child_ref = item.data(4,0)[0]
        item_ref_from_index = self.tree_list.itemFromIndex(index_of_first_child_ref)
        ref_stored_parm_indexes = item_ref_from_index.data(4,0)
        for index in ref_stored_parm_indexes:
            item_from_index = self.tree_list_parms.itemFromIndex(index)
            index_of_top_level = self.tree_list_parms.indexOfTopLevelItem(item_from_index)
            self.tree_list_parms.takeTopLevelItem(index_of_top_level)
        
    def remove_all_linked_refs(self,item):
        self.tree_list.setUpdatesEnabled(False)
        indexes = item.data(4,0)
        childs = set()
        for index in indexes: #find childs to delete
            index_string = str(index)
            position = index_string.find(" at ")
            index_string = index_string[:position]
            childs.add(self.tree_list.itemFromIndex(index))
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
        self.tree_list.setUpdatesEnabled(True)

    def show_parm(self):
        parm = self.link
        node = parm.node()
        hou.clearAllSelected()
        node.setSelected(True)
        
    def show_item(self):
        webbrowser.open(os.path.dirname(self.ref))        