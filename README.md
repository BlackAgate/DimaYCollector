# hipcollector

_upd 30.10.2024: I fixed a rare bug with sequences when you had one node pointed to the full sequence and another node only to a one file from the sequence. This may raise an error, so I fixed it with adding recursive ref search, now they process correctly_

Extended collector for Houdini. Tested in Houdini 19.5, 20.0 and 20.5.
The collector is built as an internal tool for freelancers and outsource teams. With this collector one can easily collect the entire scene in a separate folder.

The collector has two modes:
1. **Collect to folder**. Collects all scene dependencies into the specified folder and changes all the paths inside the scene, so they will be constructed from $HIP, if they hasn't already been. Copies updated scene to the same folder. **The original scene does not change!** This mode is suitable for uploading a scene to a render farm, archiving a project, or giving it to another team. Another point is to have only necessary assets in a folder, in case you have a lot of unused ones in your HIP folder.
2. **Collect to current HIP project.** Copies all scene dependencies to the current HIP scene folder and changes assosiated paths so they are constructed from $HIP if necessary. This operation changes the current scene but can be undone in one click (except the files remain copied). This mode is suitable when you work in a team cloud and want to be sure you don't have any files remain local.

Features:
- Collects all scene textures, alembics, bgeos etc.
- Shows size of each element and a total size
- Inspect, open and remove unnecessary references, sequences and parameters in one click from ui
- Works with filecache nodes in both constructed and explicit modes
- Works with sequences
- Works with UDIMs
- Works with USD including recursive search of nested usds
- Case-insensitive

USD-parser module was obtained from the Alexey Garifov Houdini Collector, thanks to him. The main idea of this collector was also inspired by his code, but the tool itself is completely different and new.

- Note: only references within the scene frame range will be parsed and copied. It means that if you have sequence 1-1000 and the frame range is 1-100, only 100 pictures will be copied. Adjust frame range correctly. Usually you'll need a full frame range of all your render nodes.
- Note2: collector will parse and copy renders from the OUT nodes by default. Delete them from list if you don't need them.
![Screenshot 2024-10-27 162333](https://github.com/user-attachments/assets/1c89d5ba-6dc3-4c12-a6b0-c721ad2446ad)
![usd](https://github.com/user-attachments/assets/61825593-da0a-4433-8438-14d9c8858031)

Known restrictions / issues:
- USD works but needs more testing
- Only Windows tested
- There is a known restriction for /out context: the collector will not read the Mantra outputs. It partitially supports Redshift_ROP nodes, but with random. I don't care about it though, as I never want to copy render files somewhere (and as compositing soft has its own collectors).
- Sequences parse only within a project playbar frame range, change it accordingly if you need
- Only references from nodes are supported (from node's parameters). If you built a custom string reference and stored it somewhere in geo attributes the collector will not see it.

How to install:
1. Download the contents of this repository as ZIP
2. Unzip the contents of the archive into your Houdini home folder (e.g. `C:\Users\<USER>\Documents\houdini19.5`) so as a result you will have `C:\Users\<USER>\Documents\houdini19.5\DimaYCollector`
3. Pick one file `DimaYCollector.json` from there and move it into packages folder of your houdini user directory (create it if it does not exist). The full path for example can look like `C:\Users\<USER>\Documents\houdini19.5\packages\DimaYCollector.json`
4. After Houdini launch, find a new DimaYCollector shelf and a single tool "DimaYCollector" on it.
5. Enjoy!
