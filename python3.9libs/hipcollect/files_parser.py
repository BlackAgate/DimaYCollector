import hou, os
from hipcollect import saver
from hipcollect.ui.utility import clean_dirname
import importlib

def filecache_parse(parm,item,target_dir,mode,tree_list):
    importlib.reload(saver)
    filecache_node = parm.node()
    filemethod = filecache_node.parm("filemethod").eval()
    ref_indexes = item.data(5,0)
    refs = set()
        
    for index in ref_indexes:
        ref_item = tree_list.itemFromIndex(index)
        ref = ref_item.data(5,0)
        refs.add(ref)
    if filemethod == 0: #if constructed filecache
        ref_temp = parm.eval()
        collapsed_ref = hou.text.collapseCommonVars(ref_temp,vars=["$HIP"])
        if "$HIP" in collapsed_ref:
            if "$HIP" not in filecache_node.parm("basedir").rawValue():
                dirname = os.path.dirname(collapsed_ref)
                basename = filecache_node.parm("basename").eval()
                index = dirname.find(basename)
                newstring = dirname[:-(len(dirname)-(index-1))]
                file_dir = dirname[4:]
                file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
                saver.saver(refs,file_target_dir,mode)
                filecache_node.parm("basedir").set(newstring)
            else:
                if mode == "folder":
                    file_dir = os.path.dirname(collapsed_ref)[4:]
                    file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
                    saver.saver(refs,file_target_dir,mode)
        else:
            current_basedir = filecache_node.parm("basedir").eval()
            file_dir = os.path.dirname(collapsed_ref)
            file_dir = file_dir.replace(current_basedir,"geo")
            file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
            saver.saver(refs,file_target_dir,mode)
            filecache_node.parm("basedir").set("$HIP/geo")
    else: #if explicit filecache
        ref_temp = filecache_node.parm("file").eval()
        unexpanded_ref = filecache_node.parm("file").unexpandedString()
        collapsed_ref = hou.text.collapseCommonVars(ref_temp,vars=["$HIP"])
        if "$HIP" in collapsed_ref:
            file_dir = os.path.dirname(collapsed_ref)
            file_dir = file_dir[4:]
            file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
            saver.saver(refs,file_target_dir,mode)
        else:     
            if "$JOB" in unexpanded_ref:                                    
                file_dir = "/geo"+os.path.dirname(unexpanded_ref)[4:]
                file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
                saver.saver(refs,file_target_dir,mode)
                newstring = unexpanded_ref.replace("$JOB","$HIP/geo")
                filecache_node.parm("file").set(newstring)
            else:
                file_dir = os.path.dirname(ref_temp)
                file_dir = "geo"+os.path.splitdrive(file_dir)[1]
                file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
                saver.saver(refs,file_target_dir,mode)
                basename = os.path.basename(unexpanded_ref)
                newstring = "$HIP/"+file_dir+"/"+basename
                filecache_node.parm("file").set(newstring)
        
def allfiles_parse(parm,item,target_dir,mode,tree_list):
    importlib.reload(saver)
    ref_temp = parm.eval()
    collapsed_ref = hou.text.collapseCommonVars(ref_temp,vars=["$HIP"])
    unexpanded_ref = parm.rawValue()
    ref_indexes = item.data(5,0)
    refs = set()
    for index in ref_indexes:
        ref_item = tree_list.itemFromIndex(index)
        ref = ref_item.data(5,0)
        refs.add(ref)
    if ".usd" not in unexpanded_ref:
        if "$HIP" in collapsed_ref:
            if "$HIP" in unexpanded_ref:
                file_dir = os.path.dirname(collapsed_ref)[4:].lower()
                file_target_dir = ""
                if file_dir:
                    file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
                else:
                    file_target_dir = target_dir
                saver.saver(refs,file_target_dir,mode)
            else:
                basename = os.path.basename(unexpanded_ref)
                dirname = os.path.dirname(ref_temp)
                combinedname = dirname+"/"+basename
                newstring = hou.text.collapseCommonVars(combinedname,vars=["$HIP"])
                file_dir = os.path.dirname(collapsed_ref)[4:].lower()
                file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
                saver.saver(refs,file_target_dir,mode)
                parm.set(newstring)
        else:
            file_dir = os.path.dirname(ref_temp)
            file_dir = "collect"+os.path.splitdrive(file_dir)[1].lower()
            file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
            basename = os.path.basename(unexpanded_ref)
            newstring = "$HIP/"+file_dir+"/"+basename
            saver.saver(refs,file_target_dir,mode)
            parm.set(newstring)
    else: #if usd
        file_dir = os.path.dirname(ref_temp)
        file_dir = "collect"+os.path.splitdrive(file_dir)[1].lower()
        file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
        basename = os.path.basename(unexpanded_ref)
        newstring = "$HIP/"+file_dir+"/"+basename
        saver.saver([ref_temp],file_target_dir,mode)
        for ref in refs:
            file_dir = os.path.dirname(ref)
            file_dir = "collect"+os.path.splitdrive(file_dir)[1].lower()
            file_target_dir = os.path.join(target_dir,clean_dirname(file_dir))
            saver.saver([ref],file_target_dir,mode)
        parm.set(newstring)