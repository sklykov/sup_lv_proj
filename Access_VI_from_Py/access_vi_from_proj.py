# -*- coding: utf-8 -*-
"""Launching LabVIEW and testing access of variables of VI from the project as the COM (ActiveX) object."""

# %% Global imports
import win32com.client
from pathlib import Path
import time

# %% Dev. Notes
# 1) Hint: https://stackoverflow.com/questions/70114011/controlling-vi-inside-of-project-from-python-via-com-activex
# 2) Access is possible to the typedef control value, but it's not causing the live update of the value on the Main.vi
# 3) SubVI below from the folder can be accessed directly, not through the lvproject handle
#    3.1) For accessing VI: Project Pane: Tools -> Options... -> VI Server -> Exported VIs -> Add (provide the name of vi)
# 4) If the subVI stored in subfolder in the project, it cannot be accessed through the call project_ref.GetVIReference(vi_path)
# 5) Apparently, if the VI accessed not through the project reference but directly, it is not communicating with the calling Main VI
# 6) Accessing and setting the indicator on the Front Panel of Main.vi is possible even without exporting it through the VI Server
# Conclusion: VI is accessible for the getter / setter from here if it isn't used as the subVI in the another VI

# %% Testing functionality
lv = win32com.client.Dispatch("Labview.Application")
print("Launched LabVIEW year:", lv.VersionYear)
lv._FlagAsMethod("OpenProject")  # necessary step from the hint (above link)
current_path = Path(__file__).parent; project_path = str(current_path.joinpath("Test_Communication_Py.lvproj"))
vi_path = str(current_path.joinpath("Main.vi")); ctl_py = current_path.joinpath("ctrls").joinpath("Flags.ctl")
lvproject = lv.OpenProject(project_path).Application  # right reference (from the hint (Dev. Notes))
main_vi = lvproject.GetVIReference(vi_path)
# py_connected = main_vi.GetControlValue("Py Connected")  # Error: parameter not found in the VI's connector pane (only on Block Diagram)
main_indicator = main_vi.GetControlValue("Script Connected")
print("Indicator on the Main VI:", main_indicator)
if main_indicator:
    main_vi.SetControlValue("Script Connected", False)

# Access and change value on the *ctl - working but not updating the typedef used on the block diagram
test_ctl_value = False  # flag for testing
if test_ctl_value and ctl_py.exists():
    ctl_py = lvproject.GetVIReference(str(ctl_py))
    py_connected = ctl_py.GetControlValue("Py Connected")
    if not py_connected:
        ctl_py.SetControlValue("Py Connected", True)

# Access and change control value on special subVI that should cause the event on the Main.vi
test_subvi_value = False  # flag for testing
subvi_path = current_path.joinpath("subVIs").joinpath("ComPy.vi")
if test_subvi_value and subvi_path.exists():
    # subvi_ref = lvproject.GetVIReference(str(subvi_path))  # Tested: throw an error, access denied even if it was added in exported VIs
    subvi_ref = lv.GetVIReference(str(subvi_path))  # If exported through as in the 3.1
    py_script_connected = subvi_ref.GetControlValue("Py Script Connect")
    if not py_script_connected:
        print("Setting True value")
        subvi_ref.SetControlValue("Py Script Connect", True)
        py_script_connected = subvi_ref.GetControlValue("Py Script Connect")
        print("Get the value:", py_script_connected)
        time.sleep(2.5)
    if py_script_connected:
        subvi_ref.SetControlValue("Py Script Connect", False); time.sleep(2.5)

# Access subVI stored in the root folder of the project through the project reference
test_subvi_in_proj = False  # flag for testing
subvi_path = current_path.joinpath("compy.vi")
if test_subvi_in_proj and subvi_path.exists():
    # subvi_ref = lvproject.GetVIReference(str(subvi_path))  # Error: same, the access denied
    subvi_ref = lv.GetVIReference(str(subvi_path))
    py_script_connected = subvi_ref.GetControlValue("Py Script Connect")
    if not py_script_connected:
        subvi_ref.SetControlValue("Py Script Connect", True)
        py_script_connected = subvi_ref.GetControlValue("Py Script Connect")
        print("Get the value:", py_script_connected); time.sleep(2.5)
