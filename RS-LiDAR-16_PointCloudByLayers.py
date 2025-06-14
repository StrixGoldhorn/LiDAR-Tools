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
Generates each layer of each user-defined frame (one frame every 360 degrees), saves to user-defined folder.

How to use:
Upload pcap of LiDAR ethernet stream to same folder as this file
Change PCAP_FILENAME to the pcap name.
Change IMAGE_FOLDER_NAME to the folder name. Point cloud images will be saved under IMAGE_FOLDER_NAME/PointCloudByLayer/LayerXY, where XY is the layer number.

Change X_START, X_END, Y_START, Y_END, Z_MAX accordingly to fit data required.
Change TARGET_FRAME_START and TARGET_FRAME_END accordingly to choose desired frames
'''

import dpkt
from math import sin, cos, radians
import matplotlib.pyplot as plt
import os


X_START = -4        # Min X coords (left)
X_END = 1           # Max X coords (right)
Y_START = -3        # Min Y coords (bottom)
Y_END = 2           # Max Y coords (top)
TARGET_FRAME_START = 65 # Frame to start processing (inclusive)
TARGET_FRAME_END = 105  # Frame to stop processing (inclusive)
DATA_FOLDER_NAME = "foldername"           # Where data of images of point cloud is saved (relative to this file)
PCAP_FILENAME = "foldername/pcapfilename.pcap"    # Filename of input pcap file (relative to this file)



def print_packets(pcap: dpkt.pcap.Reader):
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

# Global vars
cnt = 1
all_coords = [[] for i in range(16)]
theta = []

def process_pkt(pktdata):
    """Print out information for returned values

       Args:
           pktdata: packet data (dpkt.ethernet.Ethernet(buf).data.data.data)
    """
    global DATA_FOLDER_NAME, PCAP_FILENAME
    global cnt, all_coords
    
    # Extract datablocks, each datablock starts with 0xffee
    datablocks = []
    idxlist = [42, 142, 242, 342, 442, 542, 642, 742, 842, 942, 1042, 1142]
    for idx in idxlist:
        datablocks.append(pktdata[idx:idx+100])
    
    # Process each datablock
    for block in datablocks:
        
        azimuth1 = get_azimuth(block[2:4])
        azimuth2 = (azimuth1 + 0.35) % 360
        
        # If complete 1 360deg turn, add new frame
        if (0.01< azimuth1 < 0.1 or 0.01< azimuth2 < 0.1) and len(all_coords[0]) > 10:
            
            # Check if target frames are set
            if TARGET_FRAME_START and TARGET_FRAME_END != None:
            # Check if within target frame, else can skip
                if TARGET_FRAME_START <= cnt and TARGET_FRAME_END >= cnt:
                    for i in range(16):
                        generateFrames(all_coords[i], i)
                else:
                    print(f"Skipping frame {cnt}" + " "*35, end="\r")
                        
            # Else if no target frames set, just run all        
            else:
                for i in range(16):
                        generateFrames(all_coords[i], i)
            # Reset values
            cnt += 1
            all_coords = [[] for i in range(16)]
        
        # split into both returns, return 2 will have +0.35deg
        return1 = block[4:52]
        return2 = block[52:]
        channellist = [-15, -13, -11, -9, -7, -5, -3, -1, 15, 13, 11, 9, 7, 5, 3, 1]
        
        for i in range(0, len(return1), 3):
            coords = polar_to_cartesian(return1[i:i+3], azimuth1, channellist[i//3])
            all_coords[i//3].append(coords)
                
        for i in range(0, len(return2), 3):
            coords = polar_to_cartesian(return2[i:i+3], azimuth2, channellist[i//3])
            all_coords[i//3].append(coords)

def generateFrames(plane_coords: list[tuple[float, float]], plane: int):
    global cnt, DATA_FOLDER_NAME
    
    # Create data list
    x = [i[0] for i in plane_coords]
    y = [i[1] for i in plane_coords]
    
    # Plot
    fig, ax = plt.subplots()
    ax.scatter(x, y, marker=".", s=0.4)
    
    # Set marker limits
    ax.set_xlim(X_START, X_END)
    ax.set_ylim(Y_START, Y_END)
    
    # Set title
    ax.set_title(f'Frame {str(cnt).zfill(3)}')
    # plt.show()
    
    # Save and close plot
    plt.savefig(fname = f"{DATA_FOLDER_NAME}/PointCloudByLayers/Layer{str(plane).zfill(2)}/{str(cnt).zfill(3)}")
    print(f"Saved in: {DATA_FOLDER_NAME}/PointCloudByLayers/Layer{str(plane).zfill(2)}/{str(cnt).zfill(3)}", end="\r")
    plt.close()

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

def createDirectories(DATA_FOLDER_NAME: str):
    """ Creates directories for files to be saved in.
        
        Args:
            READ_FOLDER_NAME: Folder name of folder where data files are stored
    """
    try:
        os.mkdir(f"{DATA_FOLDER_NAME}/PointCloudByLayers")
        print(f"Directory '{DATA_FOLDER_NAME}/PointCloudByLayers' created successfully.")
    except FileExistsError:
        print(f"Directory '{DATA_FOLDER_NAME}/PointCloudByLayers' already exists.")
        
    for i in range(16):
        try:
            os.mkdir(f"{DATA_FOLDER_NAME}/PointCloudByLayers/Layer{str(i).zfill(2)}")
            print(f"Directory '{DATA_FOLDER_NAME}/PointCloudByLayers/Layer{str(i).zfill(2)}' created successfully.")
        except FileExistsError:
            print(f"Directory '{DATA_FOLDER_NAME}/PointCloudByLayers/Layer{str(i).zfill(2)}' already exists.")
        

def main():
    createDirectories(DATA_FOLDER_NAME)

    """Open up a test pcap file and print out the packets"""
    with open(PCAP_FILENAME, 'rb') as f:
        print("Opened file")
        pcap = dpkt.pcap.Reader(f)
        print_packets(pcap)
    
    print(f"\nFinished processing {cnt-1} frames")    
    

if __name__ == '__main__':
    main()