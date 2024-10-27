# hipcollector
Extended collector for Houdini. Tested in Houdini 19.5 and above.

The collector has two modes:
1. Collects all scene dependencies into the specified folder, and inside the scene changes all the paths, so they will be constructed from $HIP, if they hasn't already been like this. Copies updated scene to the same folder. The original scene does not change!
2. Copies all scene dependencies to the current HIP scene folder and changes assosiated paths so they are constructed from $HIP if necessary. This operation changes the current scene but can be undone in one click (except the files remain copied).

Features:
- Works with filecache nodes in both constructed and explicit modes
- Works with sequences
- Works with UDIMs
- Case-insensitive
- Remove unnecessary references, sequences and parameters in one click

Known restrictions / issues:
USD didn't tested and maybe doesn't work
Only Windows tested
There is a known restriction for /out context: the collector will not read the Mantra outputs. It partitially supports Redshift_ROP nodes, but with random. I don't care about it though, as I never want to copy render files somewhere (and as compositing soft has its own collectors).
