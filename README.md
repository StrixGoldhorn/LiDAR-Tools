# LiDAR Tools
A collation of little tools I created to help me in the processing/intepreting of LiDAR data (ie point clouds).

## LiDARs used
| Brand         | LiDAR             | Tools                     | Desc      |
|-----          |-----              |-----                      |-----      |
| Robosense     | RS-LiDAR-16       | RS-LiDAR-16_PointCloud.py | Generates 3D point cloud from captured packets          |

## RS-LiDAR-16_PointCloud.py
[This tool](./RS-LiDAR-16_PointCloud.py) helps to generate 3D point cloud from packets captured from a Robosense RS-LiDAR-16.

#### Dependencies

This relies on the `matplotlib`, `cv2`, and `dpkt` library, which can be installed using:

`pip install matplotlib`

`pip install opencv-python`

`pip install dpkt`

#### What this does

- Reads user-provided pcap file.

- Generates each frame (one frame every 360 degrees), saves to user-defined folder.

- Combines frames into video.

#### How to use

1. Upload pcap of the LiDAR ethernet stream to the same folder as the tool, change `PCAP_FILENAME` to the pcap name.

2. Create folder for point cloud images, change `IMAGE_FOLDER_NAME` to the folder name.

3. Change `VIDEO_NAME` to desired name.

4. Change `X_MAX`, `Y_MAX`, `Z_MAX` accordingly to fit data required.

5. (Optioinal) Set `IGNORE_OUT_OF_RANGE` to `True` to reduce calculations required.