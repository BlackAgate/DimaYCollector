# hipcollector

**upd 07.10.2025:**

_fixed_: small case with UDIMs selection list (now it treats them as a sequence)

added a description of how the collector works internally (check at the end of this file)

**upd 05.10.2025:**

_added:_
Console verbose added (currently processing item)

_fixed:_
1. The collector now correctly collects files from the scene very root (where the $HIP lays). In a previous version it caused an error, fixed now.
2. Fixed a small error case with Filecache nodes in an explicit mode.

**upd 03.12.2024:**

_fixed two things:_
1. _Fixed problem with copying files with "read only" attribute turned on (now it checks if file already exists and does not copy it)_
2. _Improved detecting parameter referencing algorithm so it will not try to change some custom expressions (now it searches for "chs(*)" matches in a raw value of the parm)_

This is an extended scene collector for houdini. Extended means that it not only collects all files but also fixes all paths is a scene, so the collected scene is ready to open-and-work, no need to reassign assets! I use this collector on an ongoing basis. Tested in Houdini 19.0, 19.5, 20.0, 20.5.

The collector has two modes:
1. **Collect to folder**. Collects all scene dependencies into the specified folder and changes all paths inside the scene, so they will be constructed from $HIP. Copies updated scene to the same folder. An original scene does not change. Use this mode for sending a scene to another computer or directory (uploading a scene to a render farm, archiving a project, giving it to another team).
2. **Collect to current HIP project.** Copies all scene dependencies to a current HIP scene folder and changes assosiated paths so they are constructed from $HIP if necessary. Use this mode if you don't need to collect the whole project and just want to copy all necessary files into the current HIP folder.

Features:
- Collect all scene textures, alembics, bgeos etc.
- Check size of each element and a total size
- Easy informative UI:
  - manually remove assets or parameters from collecting (including one-click sequences)
  - open asset folders or see source nodes
  - see which node uses which reference
- Works with filecache nodes in both constructed and explicit modes
- Works with sequences
- Works with UDIMs
- Works with USD including recursive search of nested usds
- Case-insensitive

USD-parser module was obtained from the Alexey Garifov Houdini Collector, thanks to him.

- Note: when working with frame-dependent sequences (usually constructed from $F) only references within the scene frame range will be parsed and copied. For example you have a JPEG file sequence with a range 1-1000 and a scene frame range is 1-100, then only 100 JPEGs will be copied (don't expect the collector to copy an unused part of a sequence). Adjust frame range in necessary. Usually you need a full frame range of all your render nodes.
- Note2: collector will try to parse and copy from the OUT context by default. Usually you don't need this, so just remove them from a list manually, or delete these nodes before collecting to save parsing time
![Screenshot 2024-10-27 162333](https://github.com/user-attachments/assets/1c89d5ba-6dc3-4c12-a6b0-c721ad2446ad)
![usd](https://github.com/user-attachments/assets/61825593-da0a-4433-8438-14d9c8858031)

Known restrictions / issues:
- Only Windows tested
- There is a known restriction/bug for /out context: sometimes Mantra and Redshift ROP nodes are not parsed. But it's not a real problem because usually you don't need them.
- Only parameter references supported (like in a normal pipeline, no custom VEX path attributes existing only in a code).

**How to install:**
1. Download the contents of this repository as ZIP
2. Unzip the contents of the archive into your Houdini home folder (e.g. `C:\Users\<USER>\Documents\houdini19.5`) so as a result you will have `C:\Users\<USER>\Documents\houdini19.5\DimaYCollector-main`
4. Pick one file `DimaYCollector.json` from there and move it into packages folder of your houdini user directory (create it if it does not exist). The full path for example can look like `C:\Users\<USER>\Documents\houdini19.5\packages\DimaYCollector.json`
5. After Houdini launch, find a new DimaYCollector shelf and a single tool "DimaYCollector" on it.
6. Enjoy!

**How this collector works internally:**

_On Collector icon clicking:_

1. It founds all parameters with references in each frame, check if they are valid ((main.py, houdini_parser.py, hip_parser.py)
2. Transfers a list of all found parameters to a QT-module and build a parameter list there (main.py, dialog.py, listviewparms.py)
3. Takes each parameter, searches for references from it in each frame, creates a second list and fills it with these references. Every reference also stores an original parameter in custom data (main.py, dialog.py, listview.py, usd_parser.py)
4. Creates additional handles: remove and inspect buttons, connects two lists with each other (button.py, utility.py)

_On "Collect to folder" button clicking:_

1. Starts processing every found parameter from a first list and gets a full list of references from them (dialog.py, files_parser.py)
2. Process through the references and decides for each reference which folders to create and which files to copy (files_parser.py)
3. If necessary, changes a path in the connected to the reference parameter, so it points to a new folder (files_parser.py)
4. Copies files to new folders (saver.py)
