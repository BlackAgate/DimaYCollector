import hou
import os
import glob

def get_parms():
    parms = set()
    for parm, none in hou.fileReferences():
        if parm:
            if parm.name() == "descriptivelabel": #special case of filecache nodes as they are special
                filecache_node = parm.node()
                filecache_node_parm = filecache_node.parm("sopoutput")
                parms.add(filecache_node_parm)
                continue
        if not parm or not parm.eval():
            continue
        if parm != parm.getReferencedParm(): #excludes references
            continue
        if parm.node().type().nameComponents()[2] == "filecache": #excludes filecache nodes because they were already got above
            continue
        parms.add(parm)
    return parms
    
def ref_convert(parm, frame, path=None): #frame by frame
    ref = os.path.abspath(hou.text.expandString(parm.evalAtFrame(frame)))
    ref = ref.lower()
    valid = 1
    if os.path.isfile(ref):
        ref = ref.replace("\\", "/")
    else:
        if "<udim>" in ref:
            if len(glob.glob(ref.replace("<udim>", "*"))) == 0:
                valid = 0
            else:
                ref = ref.replace("\\", "/")
        else:
            valid = 0
    return ref, valid
       
def parse(valid_parms,frame):
    refs = set()
    parms = set()
    for parm in valid_parms:
        ref, valid = ref_convert(parm, frame=frame)
        if valid == 0:
            continue
        if ref in refs:
            if parm in parms:
                continue
            parms.add(parm)
            continue
        refs.add(ref)
        parms.add(parm)
    return parms
       
def total_size(parms):
    start_frame = int(hou.playbar.frameRange()[0])
    end_frame = int(hou.playbar.frameRange()[1])
    
    refs_for_size = set()
    size = 0
    for frame in range(start_frame, end_frame + 1, 1):
        for parm in parms:
            ref, valid = ref_convert(parm,frame)
            if valid:
                if ref not in refs_for_size:
                    size += os.path.getsize(ref)
                    refs_for_size.add(ref)
    return size