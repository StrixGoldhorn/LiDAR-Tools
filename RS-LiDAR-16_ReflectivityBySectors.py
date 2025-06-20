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






For Robosense RS-LiDAR-16

What this does:
Reads user-provided pcap file.
Plots graph of ratio of points with user-defined reflectivity, to total amount of points, in a given sector.
Number of sectors of a point cloud is user-defined, under `NUM_SECTORS`. Each sector will be NUM_SECTORS/360 degrees.
Threshold values are user-defined, under `ratios`.

How to use:
Change TARGET_FRAMES to array of integers of frames to plot in graph
Change ROOT_FOLDER_NAME to the folder name to where data will be stored.
Upload pcap of LiDAR ethernet stream to same folder as this file, change PCAP_FILENAME to the pcap name.

Change NUM_SECTORS to desired number of sectors
Change ratios to 6 reflectivity values to set as threshold
'''

import dpkt
from math import sin, cos, radians
import matplotlib.pyplot as plt
import numpy as np
import os
  
TARGET_FRAMES = [x for x in range(180)] # Frames to plot in graph
ROOT_FOLDER_NAME = "FOLDER_NAME"    # Where folder of frames of point cloud will be saved
PCAP_FILENAME = "FOLDER_NAME/FILENAME.pcap"    # Filename of input pcap file

NUM_SECTORS = 4    # Number of sectors

ratios = [32, 64, 96, 128, 160, 192]    # Threhold reflectivity values (0-256)



def plot_frame_intensities(log_data, sector_num):
    # Parse the log data
    lines = log_data.strip().split('\n')
    frame_numbers = []
    intensity1 = []
    intensity2 = []
    intensity3 = []
    intensity4 = []
    intensity5 = []
    intensity6 = []

    for line in lines:
        parts = line.split('|')
        frame_part = parts[0].strip()
        frame_num = int(frame_part.split()[1])  # Extract frame number
        frame_numbers.append(frame_num)
        intensity1.append(float(parts[1].strip()))
        intensity2.append(float(parts[2].strip()))
        intensity3.append(float(parts[3].strip()))
        intensity4.append(float(parts[4].strip()))
        intensity5.append(float(parts[5].strip()))
        intensity6.append(float(parts[6].strip()))

    # Plotting
    plt.figure(figsize=(12, 6))
    
    # Plot each intensity column
    plt.plot(frame_numbers, intensity1, label = ratios[0])
    plt.plot(frame_numbers, intensity2, label = ratios[1])
    plt.plot(frame_numbers, intensity3, label = ratios[2])
    plt.plot(frame_numbers, intensity4, label = ratios[3])
    plt.plot(frame_numbers, intensity5, label = ratios[4])
    plt.plot(frame_numbers, intensity6, label = ratios[5])

    # Formatting the plot
    plt.xlabel('Frame Number')
    plt.ylabel('Ratio of reflectivity x')
    plt.ylim([0, 1])
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # plt.show()
    plt.savefig(fname = f"{ROOT_FOLDER_NAME}/ReflectivityRatioGraphs/sector{sector_num}")


class Frame:
    DEG_PER_SECTOR = 360 // NUM_SECTORS
    
    def __init__(self, data: np.array):
        self.sector_illum_data = self.init_illum_data(data)
        
    def init_illum_data(self, data: np.array):
        output = []
        for i in range(0, 360, self.DEG_PER_SECTOR):
            filtered = data[(data[:, 1] >= i) & (data[:, 1] <= i+self.DEG_PER_SECTOR)]
            output.append(filtered)
        return output
    
    def get_reflectivity_ratio(self, sector_num: int, threshold: int):
        count = np.sum(self.sector_illum_data[sector_num][:, 3] > threshold)
        return count / self.sector_illum_data[sector_num][:, 3].size
    
    def write_to_log(self, frame_num: int, sector_num: int):
        a = self.get_reflectivity_ratio(sector_num, ratios[0])
        b = self.get_reflectivity_ratio(sector_num, ratios[1])
        c = self.get_reflectivity_ratio(sector_num, ratios[2])
        d = self.get_reflectivity_ratio(sector_num, ratios[3])
        e = self.get_reflectivity_ratio(sector_num, ratios[4])
        f = self.get_reflectivity_ratio(sector_num, ratios[5])
        
        with open(f"{ROOT_FOLDER_NAME}/DetectAttack/log{str(sector_num).zfill(3)}", "a") as file:
            file.write(f"Frame {str(frame_num).zfill(3)} | {str(a)} | {str(b)} | {str(c)} | {str(d)} | {str(e)} | {str(f)} \n")


def print_packets(pcap):
    """Print out information about each packet in a pcap

        Adapted from: https://github.com/kbandla/dpkt/blob/master/examples/print_packets.py

       Args:
           pcap: dpkt pcap reader object (dpkt.pcap.Reader)
    """
    # For each packet in the pcap process the contents
    for timestamp, buf in pcap:

        # Unpack the Ethernet frame (mac src/dst, ethertype)
        eth = dpkt.ethernet.Ethernet(buf)

        # Make sure the Ethernet data contains an IP packet
        if not isinstance(eth.data, dpkt.ip.IP):
            print('Non IP Packet type not supported %s\n' % eth.data.__class__.__name__)
            continue
        
        # Extract out the data, check headers before processing
        pktdata = eth.data.data.data
        try:
            header = pktdata[0:42]
            # print(f"Header: {header[0:8].hex()}")
            if header[0:8].hex() == "55aa050a5aa550a0":
                process_pkt(pktdata)
        except:
            pass

cnt = 1
frame_data = np.array([0, 0, 0, 0]) # distance, horiz_angle, vert_angle, intensity
all_frames = []

def data_to_Frame_obj(frame_data: np.array):
    """Converts np.array to Frame object

       Args:
           frame_data: np.array of [distance, horiz_angle, vert_angle, intensity] of each angle
    """
    frame_data = frame_data[1:]
    f = Frame(frame_data)
    all_frames.append(f)

def write_all_frames_to_log():
    for i in range(len(all_frames)):
        for j in range(NUM_SECTORS):
            all_frames[i].write_to_log(i, j)

def process_pkt(pktdata):
    global ROOT_FOLDER_NAME, PCAP_FILENAME
    global cnt, frame_data
    """Print out information for returned values

       Args:
           pktdata: packet data (dpkt.ethernet.Ethernet(buf).data.data.data)
    """
    
    # Extract datablocks, each datablock starts with 0xffee
    datablocks = []
    idxlist = [42, 142, 242, 342, 442, 542, 642, 742, 842, 942, 1042, 1142]
    for idx in idxlist:
        datablocks.append(pktdata[idx:idx+100])
    
    # Process each datablock
    for block in datablocks:
        if cnt > max(TARGET_FRAMES): return
        azimuth1 = get_azimuth(block[2:4])
        azimuth2 = (azimuth1 + 0.35) % 360
        
        # If complete 1 360deg turn, add new frame
        if (0.01 < azimuth1 < 0.5 or 0.01 < azimuth2 < 0.5) and frame_data.size > 500:
            
            # Check if target frames are set
            if len(TARGET_FRAMES) > 0:
            # Check if within target frame, else can skip
                if cnt in TARGET_FRAMES:                 
                    data_to_Frame_obj(frame_data)
                    print(f"Saved frame {str(cnt).zfill(3)}"+ " "*35)
                    
                else:
                    print(f"Skipping frame {str(cnt).zfill(3)}" + " "*35, end="\r")
                        
            # Else if no target frames set, just run all        
            else:
                print("PLEASE SET TARGET FRAMES")
            
            # Reset values
            cnt += 1
            frame_data = np.array([0, 0, 0, 0])
            
        # split into both returns, return 2 will have +0.35deg
        return1 = block[4:52]
        return2 = block[52:]
        channellist = [-15, -13, -11, -9, -7, -5, -3, -1, 15, 13, 11, 9, 7, 5, 3, 1]
        
        for i in range(0, len(return1), 3):
            distance = get_distance(return1[i:i+3][0:2])
            horiz_angle = azimuth1
            vert_angle = channellist[i//3]
            intensity = return1[i:i+3][2]
            
            temp = np.array([distance, horiz_angle, vert_angle, intensity])
            frame_data = np.vstack((frame_data, temp))
                
        for i in range(0, len(return2), 3):
            distance = get_distance(return2[i:i+3][0:2])
            horiz_angle = azimuth2
            vert_angle = channellist[i//3]
            intensity = return2[i:i+3][2]
            
            temp = np.array([distance, horiz_angle, vert_angle, intensity])
            frame_data = np.vstack((frame_data, temp))

def polar_to_cartesian(bytedata: str, horizangle: float, vertangle: float) -> tuple[float, float, float]:
    """ Returns (x, y, z) cartesian coordinates.

        Args:
           bytedata: 3-byte data to be converted (2-byte distance value, 1-byte reflectivity)
           horizangle: Horizontal angle corresponding to return
           vertangle: Vertical angle corresponding to channel
    """
    r = get_distance(bytedata[0:2])
    x = r * sin(radians(90-vertangle)) * cos(radians(horizangle))
    y = r * sin(radians(90-vertangle)) * sin(radians(horizangle))
    z = r * cos(radians(90-vertangle))
    return (x, y, z)

def get_distance(bytedata: str) -> float:
    """ Returns decimal distance value.

        Args:
           bytedata: 2-byte data to be converted
    """
    return int(bytedata.hex(), 16)/100

def get_azimuth(bytedata: str) -> float:
    """ Returns decimal azimuth value.

        Args:
           bytedata: 2-byte data to be converted
    """
    return int(bytedata.hex(), 16)/100

def createDirectories(ROOT_FOLDER_NAME: str):
    """ Creates directories for files to be saved in.
        
        Args:
            ROOT_FOLDER_NAME: Folder name of folder where data files are stored
    """
    
    try:
        os.mkdir(f"{ROOT_FOLDER_NAME}/DetectAttack/")
        print(f"Directory '{ROOT_FOLDER_NAME}/DetectAttack/' created successfully.")
    except FileExistsError:
        print(f"Directory '{ROOT_FOLDER_NAME}/DetectAttack/' already exists.")

def test():
    createDirectories(ROOT_FOLDER_NAME)

    """Open up a test pcap file and print out the packets"""
    with open(PCAP_FILENAME, 'rb') as f:
        print("Opened file")
        pcap = dpkt.pcap.Reader(f)
        print_packets(pcap)
    
    print(f"Finished adding {cnt-1}.")
    
    print(f"Writing all frames to log")
    write_all_frames_to_log()
    
    print("Drawing plots")
    for i in range(0, NUM_SECTORS):
        sector_num = str(i).zfill(3)
        with open(f"{ROOT_FOLDER_NAME}/DetectAttack/log{sector_num}", "r") as f:
            log_data= f.read()
        plot_frame_intensities(log_data, sector_num)
        print(f"Saved sector {sector_num}")
    print("Finished!")

if __name__ == '__main__':
    test()