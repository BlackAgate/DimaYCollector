import glob
import hou, os
from hipcollect.hip_parser import ref_convert
import shutil

def saver(parm,file_target_dir,mode):
    start_frame = int(hou.playbar.frameRange()[0])
    end_frame = int(hou.playbar.frameRange()[1])
    refs = set()
    if mode == "folder":
        for frame in range(start_frame, end_frame + 1, 1):
            ref,valid = ref_convert(parm,frame)
            if valid:
                if "<udim>" in ref:
                    for udim in glob.glob(ref.replace("<udim>", "*")):
                        refs.add(udim)
                else:
                    refs.add(ref)
    else:
        for frame in range(start_frame, end_frame + 1, 1):
            ref,valid = ref_convert(parm,frame,file_target_dir)
            if valid:
                if "<udim>" in ref:
                    for udim in glob.glob(ref.replace("<udim>", "*")):
                        udim = udim.replace("\\", "/")
                        target_check = file_target_dir.replace("\\", "/")+"/"+os.path.basename(udim)
                        if target_check != udim:
                            refs.add(udim)
                else:
                    target_check = file_target_dir.replace("\\", "/")+"/"+os.path.basename(ref)
                    if target_check != ref:
                        refs.add(ref)
    for ref in refs:
        file_target_dir = file_target_dir.replace("\\", "/")
        os.makedirs(file_target_dir, exist_ok=True)
        shutil.copy(ref, file_target_dir)