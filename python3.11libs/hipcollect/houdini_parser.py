import importlib
from hipcollect import hip_parser
import hou, sys

def run():
    if hou.hipFile.hasUnsavedChanges() or hou.hipFile.isNewFile():
        saving = hou.ui.displayCustomConfirmation("Please save scene before running collector",severity=hou.severityType.Message,buttons=('Save','Cancel'))
        if saving:
            sys.exit()
        else:
            hou.hipFile.save()
    with hou.InterruptableOperation("Parsing scene...",open_interrupt_dialog=True) as oper:
        oper.updateProgress(0)
        start_frame = int(hou.playbar.frameRange()[0])
        end_frame = int(hou.playbar.frameRange()[1])
        
        importlib.reload(hip_parser)
              
        valid_parms = hip_parser.get_parms()
        parms = set()
        
        for frame in range(start_frame, end_frame + 1, 1):
            oper.updateProgress(frame/end_frame)
            hip_parms = hip_parser.parse(valid_parms,frame)
            parms.update(hip_parms)
                       
        return parms