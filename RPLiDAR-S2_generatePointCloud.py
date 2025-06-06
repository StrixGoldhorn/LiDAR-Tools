'''
MIT License

Copyright (c) 2025 StrixGoldhorn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.






For SLAMTEC RSLiDAR S2

What this does:
Reads user-provided dump files (generated by SLAMTEC's FrameGrabber app demo).
Generates point cloud, saves to folder.

How to use:
Upload dump files to folder, change READ_FOLDER_NAME to the folder name.
Change FILENAME_ARR to each of the dumped data file name.
Change MAX_DIST_SHOWN accordingly to fit data required.

Set DISPLAY to True to display each point cloud before saving if required.
'''

import matplotlib.pyplot as plt
import numpy as np
import os

READ_FOLDER_NAME = "folder_with_datafiles"      # Folder with data files
FILENAME_ARR = ["control", "50khz", "100khz"]   # Names of data files
MAX_DIST_SHOWN = 2000                           # Crops graph to fit up to max distance
DISPLAY = False                                 # If true, displays each graph before saving
    
def save_pointcloud(data_arr, READ_FOLDER_NAME, READ_FILE_NAME):
    """ Saves (and optionally displays) point cloud

        Args:
            data_arr: numpy array with angle, distance, quality
            READ_FOLDER_NAME: Folder name of folder where data files are stored
            READ_FILE_NAME: Filename of data file to be processed
    """
    angle_arr = data_arr[:, 0]
    distance_arr = data_arr[:, 1]
    quality_arr = data_arr[:, 2]

    # Convert to radians, prepare to plot
    angles_rad_arr = np.deg2rad(angle_arr)

    # Plot point cloud
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    ax.scatter(angles_rad_arr, distance_arr, c=quality_arr, cmap='viridis', s=0.1)
    
    # Marking settings
    ax.grid(False, axis='y')
    ax.set_yticklabels([])
    detailed_ticks = np.arange(0, 360, 10)  # Every 5 degrees
    ax.set_xticks(np.deg2rad(detailed_ticks))
    
    # View settings
    ax.set_rmax(MAX_DIST_SHOWN)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    
    if DISPLAY == True:
        plt.show()
    
    plt.savefig(f"{READ_FOLDER_NAME}/Point Clouds/{READ_FILE_NAME}.png", dpi=300)
    print(f"Point cloud SAVED!")
    plt.close()

def main():
    # Create directory to save images
    try:
        os.mkdir(f"{READ_FOLDER_NAME}/Point Clouds")
        print(f"Directory '{READ_FOLDER_NAME}/Point Clouds' created successfully.")
    except FileExistsError:
        print(f"Directory '{READ_FOLDER_NAME}/Point Clouds' already exists.")
        
    # Iterate through each data file
    for filename in FILENAME_ARR:
        READ_FILE_NAME = filename
        data_arr = np.empty((0,3))
            
        with open(f"{READ_FOLDER_NAME}/{READ_FILE_NAME}", "r") as f:
            # Skip first 3 lines
            f.readline()
            datacount = f.readline()
            f.readline()
            
            print("-"*20)
            print(f"Viewing: {READ_FILE_NAME}")
            print(f"Total readings: {datacount[7:-1]}")
            
            # Process each line, save data appropriately
            for line in f:
                line_data = line.strip().split(" ")
                
                angle = float(line_data[0])
                distance = float(line_data[1])
                quality = int(line_data[2])

                data_arr = np.vstack([data_arr, [angle, distance, quality]])
                
        print("Generating point cloud")
        save_pointcloud(data_arr, READ_FOLDER_NAME, READ_FILE_NAME)

main()