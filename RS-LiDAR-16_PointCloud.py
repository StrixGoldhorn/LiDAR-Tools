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
Generates each frame (one frame every 360 degrees), saves to user-defined folder.
Combines frames into video.

How to use:
Upload pcap of LiDAR ethernet stream to same folder as this file, change PCAP_FILENAME to the pcap name.
Create folder for point cloud images, change IMAGE_FOLDER_NAME to the folder name.
Change VIDEO_NAME to desired name.

Change X_MAX, Y_MAX, Z_MAX accordingly to fit data required.
Set IGNORE_OUT_OF_RANGE to True to reduce calculations required.
'''

X_MAX = 3                                  # Point cloud will display from -X_MAX to +X_MAX (in meters)
Y_MAX = X_MAX                              # Point cloud will display from -Y_MAX to +Y_MAX (in meters)
Z_MAX = 1                                  # Point cloud will display from -Z_MAX to +Z_MAX (in meters)
IGNORE_OUT_OF_RANGE = True                 # If true, will not plot points out of X_MAX, Y_MAX, Z_MAX
IMAGE_FOLDER_NAME = "foldername"           # Where images of point cloud will be saved (NEED TO CREATE FOLDER BEFOREHAND)
VIDEO_NAME = "video_filename.avi"              # Filename of output video
PCAP_FILENAME = "wireshark_pcap_filename.pcap" # Filename of input pcap file

import dpkt
from math import sin, cos, radians, sqrt
import matplotlib.pyplot as plt

def print_packets(pcap):
    """ Print out information about each packet in a pcap

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
            if header[0:8].hex() == "55aa050a5aa550a0":
                process_pkt(pktdata)
        except:
            pass

cnt = 1
x = []
y = []
z = []
intensity = []

def process_pkt(pktdata):
    global X_MAX, Y_MAX, Z_MAX
    global IGNORE_OUT_OF_RANGE, IMAGE_FOLDER_NAME, VIDEO_NAME, PCAP_FILENAME
    global cnt, x, y, z, intensity
    """ Print out information for returned values

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
        
        azimuth1 = get_azimuth(block[2:4])
        azimuth2 = (azimuth1 + 0.35) % 360
        
        # If complete 1 360deg turn, add new frame
        if (0.01< azimuth1 < 0.1 or 0.01< azimuth2 < 0.1) and len(x) > 10:
            
            fig = plt.figure(figsize=(7.2, 7.2))
            ax = fig.add_subplot(projection='3d')
            # xyz as coords, . as marker, s is marker size, c is color of marker, cmap is color map which ranges from 0-255
            ax.scatter(x, y, z, marker=".", s = 1, c = intensity, cmap = "viridis")
            
            # Set plot axes limits
            ax.axes.set_xlim3d(left=-X_MAX, right=X_MAX) 
            ax.axes.set_ylim3d(bottom=-Y_MAX, top=Y_MAX) 
            ax.axes.set_zlim3d(bottom=-Z_MAX, top=Z_MAX) 
            
            # Save as image
            plt.title(f'Frame {str(cnt).zfill(3)}')
            plt.savefig(fname = f"{IMAGE_FOLDER_NAME}\{str(cnt).zfill(3)}")
            print(f"SAVED! Frame {str(cnt).zfill(3)}", end="\r")
            plt.close()
            
            # Reset values
            cnt += 1
            x = []
            y = []
            z = []
            intensity = []
        
        # split into both returns, return 2 will have +0.35deg
        return1 = block[4:52]
        return2 = block[52:]
        
        channellist = [-15, -13, -11, -9, -7, -5, -3, -1, 15, 13, 11, 9, 7, 5, 3, 1]
        
        for i in range(0, len(return1), 3):
            # If IGNORE_OUT_OF_RANGE and distance to point is more than graph display, pass
            if IGNORE_OUT_OF_RANGE and (get_distance(return1[i:i+3][0:2]) > sqrt(X_MAX**2 + Y_MAX**2 + Z_MAX**2)):
                pass
            else:
                coords = polar_to_cartesian(return1[i:i+3], azimuth1, channellist[i//3])
                
                x.append(coords[0])
                y.append(coords[1])
                z.append(coords[2])
                intensity.append(return1[i:i+3][2])
                
        for i in range(0, len(return2), 3):
            # If IGNORE_OUT_OF_RANGE and distance to point is more than graph display, pass
            if IGNORE_OUT_OF_RANGE and (get_distance(return2[i:i+3][0:2]) > sqrt(X_MAX**2 + Y_MAX**2 + Z_MAX**2)):
                pass
            else:
                coords = polar_to_cartesian(return2[i:i+3], azimuth2, channellist[i//3])
                
                x.append(coords[0])
                y.append(coords[1])
                z.append(coords[2])
                intensity.append(return2[i:i+3][2])
        
def polar_to_cartesian(bytedata, horizangle, vertangle):
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

def get_distance(bytedata):
    """ Returns decimal distance value.

        Args:
           bytedata: 2-byte data to be converted
    """
    return int(bytedata.hex(), 16)/100

def get_azimuth(bytedata):
    """ Returns decimal azimuth value.

        Args:
           bytedata: 2-byte data to be converted
    """
    return int(bytedata.hex(), 16)/100
    
def convert_to_video():
    """ Converts images in IMAGE_FOLDER_NAME to a .avi video, saved as VIDEO_NAME
    """
    import cv2
    import os

    image_folder = IMAGE_FOLDER_NAME
    video_name = VIDEO_NAME

    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 10, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()
    
def main():
    """Open up a test pcap file and print out the packets"""
    with open(PCAP_FILENAME, 'rb') as f:
        print("Opened file")
        pcap = dpkt.pcap.Reader(f)
        print_packets(pcap)
    
    print("Finished processing images")    
    convert_to_video()

if __name__ == '__main__':
    main()