# -*- coding: utf-8 -*-
"""Launching LabVIEW and testing access of variables of VI from the project as the COM (ActiveX) object."""

# %% Global imports
import win32com.client
from pathlib import Path

# %% Dev. Notes
# 1) Hint: https://stackoverflow.com/questions/70114011/controlling-vi-inside-of-project-from-python-via-com-activex
# 2) Access is possible to the typedef control value, but it's not causing the live update of the value on the Main.vi

# %% Testing functionality
lv = win32com.client.Dispatch("Labview.Application")
print("Launched LabVIEW year:", lv.VersionYear)
lv._FlagAsMethod("OpenProject")  # necessary step from the hint (above link)
current_path = Path(__file__).parent; project_path = str(current_path.joinpath("Test_Communication_Py.lvproj"))
vi_path = str(current_path.joinpath("Main.vi")); ctl_py = str(current_path.joinpath("Flags.ctl"))
lvproject = lv.OpenProject(project_path).Application  # right reference (from the hint)
main_vi = lvproject.GetVIReference(vi_path); ctl_py = lvproject.GetVIReference(ctl_py)
# py_connected = main_vi.GetControlValue("Py Connected")  # Error: parameter not found in the VI's connector pane
py_connected = ctl_py.GetControlValue("Py Connected")
if not py_connected:
    ctl_py.SetControlValue("Py Connected", True)
