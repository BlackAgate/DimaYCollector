import glob
import hou, os
from hipcollect.hip_parser import ref_convert
import shutil
        
def saver(refs,file_target_dir,mode):
    refs_to_copy = set()
    if mode == "folder":
        for ref in refs:
            if "<udim>" in ref:
                for udim in glob.glob(ref.replace("<udim>", "*")):
                    refs_to_copy.add(udim)
            else:
                refs_to_copy.add(ref)
    else:
        for ref in refs:
            if "<udim>" in ref:
                for udim in glob.glob(ref.replace("<udim>", "*")):
                    udim = udim.replace("\\", "/")
                    target_check = file_target_dir.replace("\\", "/")+"/"+os.path.basename(udim)
                    if target_check != udim:
                        refs_to_copy.add(udim)
            else:
                target_check = file_target_dir.replace("\\", "/")+"/"+os.path.basename(ref)
                if target_check != ref:
                    refs_to_copy.add(ref)
    for ref in refs_to_copy:
        file_target_dir = file_target_dir.replace("\\", "/")
        os.makedirs(file_target_dir, exist_ok=True)
        shutil.copy(ref, file_target_dir)