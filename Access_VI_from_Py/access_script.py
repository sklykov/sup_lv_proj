# -*- coding: utf-8 -*-
"""Launching LabVIEW and VI as the COM (ActiveX) object."""

# %% Global imports
import win32com.client
from pathlib import Path

# %% Testing functionality
lv = win32com.client.Dispatch("Labview.Application")
print("Launched LabVIEW year:", lv.VersionYear)
current_path = Path(__file__).parent; vi_path = str(current_path.joinpath("test_gen_noisy_array.vi"))
vi = lv.GetVIReference(vi_path)
print(vi.GetControlValue("mean"), vi.GetControlValue("Slider"))  # shows current values on the Front Panel

# Dev. Notes:
# 1) Scripts read the current displayed values on VI (updated online or displayed after vi closing);
# 2) For accessing the script values, add the vi name in: Tools > Options -> VI Server -> Exported VIs
