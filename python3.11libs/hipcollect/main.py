import importlib
from hipcollect import houdini_parser
from hipcollect.ui import dialog
from PySide2 import QtCore
import hou

def run():   
    importlib.reload(houdini_parser)
    importlib.reload(dialog)
    
    mode = hou.updateModeSetting()
    hou.setUpdateMode(hou.updateMode.Manual)
    
    parms = houdini_parser.run()
    
    t = dialog.SubmitDialog(parms)
    t.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    t.tree_list_parms.addPaths(parms)
    t.process_and_create_second_tree()
    t.update_total_size()
    if len(t.tree_list.error_files) > 0:
        formatted_list = "There are troubles with these files:\n"
        for f in t.tree_list.error_files:
            formatted_list += f + "\n"
        hou.ui.displayMessage(formatted_list)
    t.show()
    
    hou.setUpdateMode(mode)