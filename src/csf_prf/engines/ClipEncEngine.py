import os
import requests
import zipfile
import shutil
import pathlib


from osgeo import ogr


class ClipEncEngine:
    """Class to download all ENC files that intersect a project boundary shapefile"""

    def __init__(self, param_lookup: dict) -> None:
        self.input_folder = param_lookup['input_folder'].valueAsText
        self.output_folder = param_lookup['output_folder'].valueAsText
        self.driver = None

    def clip_enc_files(self, enc_sorter):
        scales = list(sorted(enc_sorter.keys()))  # 1, 2, 3, 4, 5
        for i, scale in enumerate(scales):
            if i < len(scales):
                upper_scale = i + 1
                print(scale, upper_scale)
                for lower in enc_sorter[scale]:
                    print(str(lower))
                    clipped = [self.clip_files(lower, upper) for upper in enc_sorter[upper_scale]]
                    break
    
    def clip_files(self, lower, upper):
        lower_enc = self.driver.Open(str(lower), 0)
        upper_enc = self.driver.Open(str(upper), 0)
        for lower_layer, upper_layer in zip(lower_enc, upper_enc):
            # These have Clip()
            lower_layer.ResetReading()
            upper_layer.ResetReading()
            print(lower_layer.GetName(), upper_layer.GetName())
        
    def get_enc_files(self):
        enc_files = []
        for file in os.listdir(self.input_folder):
            if file.endswith('.000'):
                enc_files.append(pathlib.Path(self.input_folder) / file)
        return enc_files
        
    def get_enc_list(self):
        enc_files = self.get_enc_files()
        enc_sorter = {}
        for enc_file in enc_files:
            scale = int(enc_file.stem[2])
            if scale not in enc_sorter.keys():
                enc_sorter[scale] = []
            enc_sorter[scale].append(enc_file)
        print(enc_sorter)
        return enc_sorter

    def start(self) -> None:
        self.driver = ogr.GetDriverByName('S57')
        enc_sorter = self.get_enc_list()
        self.clip_enc_files(enc_sorter)
        # clip by top to bottom of stacked ENCs
            # if no clip, only take features from stacked ENC order
        # output clipped ENC files to output folder