# LiDAR Tools
A collation of little tools I created to help me in the processing/intepreting of LiDAR data (ie point clouds).

## LiDARs used
| Brand         | LiDAR             | Tools                     | Desc      |
|-----          |-----              |-----                      |-----      |
| RoboSense     | RS-LiDAR-16       | [RS-LiDAR-16_PointCloud.py](#rs-lidar-16_pointcloudpy) | Generates 3D point cloud from captured packets    |
| RoboSense     | RS-LiDAR-16       | [RS-LiDAR-16_PointCloudByLayers.py](#rs-lidar-16_pointcloudbylayerspy) | Generates point cloud, separated by layers, from captured packets    |
| RoboSense     | RS-LiDAR-16       | [RS-LiDAR-16_ReflectivityBySectors.py](#rs-lidar-16_reflectivitybysectorspy) | Generates graphs of reflectivity over time    |
| SLAMTEC       | RPLiDAR S2        | [RPLiDAR-S2_generatePointCloud.py](#rplidar-s2_generatepointcloudpy) | Generates 2D point cloud from dumped data files    |
| SLAMTEC       | RPLiDAR S2        | [RPLiDAR-S2_generateAnglePlotLimited.py](#rplidar-s2_generateangleplotlimitedpy) | Generates visualisation of whether data exists at user-specified angle range  |
| SLAMTEC       | RPLiDAR S2        | [RPLiDAR-S2_generateScatterPlotLimited.py](#rplidar-s2_generatescatterplotlimitedpy) | Generates scatter plot of points within user-specified angle range  |
| SLAMTEC       | RPLiDAR S2        | [RPLiDAR-S2_combinedTools.py](#rplidar-s2_combinedtoolspy) | Compilation of my RPLiDAR S2 tools, runs as a CLI tool   |

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

## RS-LiDAR-16_PointCloudByLayers.py
[This tool](./RS-LiDAR-16_PointCloudByLayers.py) helps to generate point cloud, separated by layers, from packets captured from a Robosense RS-LiDAR-16.

#### Dependencies

This relies on the `dpkt`, `matplotlib`, `math`, and `os` library, which can be installed using:

`pip install dpkt`

`pip install matplotlib`

`math` and `os` are pre-installed as part of the Python Standard Library

#### What this does

- Reads user-provided pcap file.

- Generates each layer of each user-defined frame (one frame every 360 degrees), saves to user-defined folder.

#### How to use

1. Upload pcap of LiDAR ethernet stream to same folder as this file

2. Change PCAP_FILENAME to the pcap name.

3. Change IMAGE_FOLDER_NAME to the folder name. Point cloud images will be saved under IMAGE_FOLDER_NAME/PointCloudByLayer/LayerXY, where XY is the layer number.

4. Change X_START, X_END, Y_START, Y_END, Z_MAX accordingly to fit data required.

5. Change TARGET_FRAME_START and TARGET_FRAME_END accordingly to choose desired frames



## RS-LiDAR-16_ReflectivityBySectors.py
[This tool](./RS-LiDAR-16_ReflectivityBySectors.py) plots graph of ratio of points with user-defined reflectivity, to total amount of points, in a given sector.

#### Dependencies

This relies on the `dpkt`, `matplotlib`, `numpy`, `math`, and `os` library, which can be installed using:

`pip install dpkt`

`pip install matplotlib`

`pip install numpy`

`math` and `os` are pre-installed as part of the Python Standard Library

#### What this does

- Reads user-provided pcap file.

- Plots graph of ratio of points with user-defined reflectivity, to total amount of points, in a given sector.

- Number of sectors of a point cloud is user-defined, under `NUM_SECTORS`. Each sector will be NUM_SECTORS/360 degrees.

- Threshold values are user-defined, under `ratios`.

#### How to use

1. Change TARGET_FRAMES to array of integers of frames to plot in graph

2. Change ROOT_FOLDER_NAME to the folder name to where data will be stored.

3. Upload pcap of LiDAR ethernet stream to same folder as this file, change PCAP_FILENAME to the pcap name.

4. Change NUM_SECTORS to desired number of sectors

5. Change ratios to 6 reflectivity values to set as threshold

Assuming your pcap files is `capture.pcap`, your file structure should look like this.

```
main
| --- ROOT_FOLDER_NAME
| | --- capture.pcap
|
| --- RS-LiDAR-16_ReflectivityBySectors.py
```

After running the program, your file structure will look like this


```
main
| --- ROOT_FOLDER_NAME
| | --- capture.pcap
| |
| | --- DetectAttack
| | | --- log000
| | | --- log001
| | | --- log002
| | | --- log003
| |
| | --- ReflectivityRatioGraphs
| | | --- sector000.png
| | | --- sector001.png
| | | --- sector002.png
| | | --- sector003.png
| |
| --- RS-LiDAR-16_ReflectivityBySectors.py
```



## RPLiDAR-S2_generatePointCloud.py
[This tool](./RPLiDAR-S2generate_PointCloud.py) helps to generate 2D point cloud from data dumps from SLAMTEC's FrameGrabber application of a SLAMTEC RPLiDAR S2.

#### Dependencies

This relies on the `matplotlib`, `numpy`, and `os` library, which can be installed using:

`pip install matplotlib`

`pip install numpy`

`os` is pre-installed as part of the Python Standard Library

#### What this does

- Reads folder of user-provided data files dumped from the FrameGrabber application.

- Generates point clouds from data files, saves to folder.

#### How to use

1. Upload dump files to folder, change READ_FOLDER_NAME to the folder name.

2. Change FILENAME_ARR to each of the dumped data file name.

3. Change MAX_DIST_SHOWN accordingly to fit data required.

4. (Optional) Set DISPLAY to True to display each point cloud before saving if required.

Assuming your dumped files are `control`, `50khz`, and `100khz`, your file structure should look like this.

```
main
| --- folder_with_datafiles
| | --- control
| | --- 50khz
| | --- 100khz
|
| --- RPLiDAR-S2_generatePointCloud.py
```

After running the program, your file structure will look like this

```
main
| --- folder_with_datafiles
|  | --- control
|  | --- 50khz
|  | --- 100khz
|  |
|  | --- Point Clouds
|  |  | --- control.png
|  |  | --- 50khz.png
|  |  | --- 100khz.png
|
| --- RPLiDAR-S2_generatePointCloud.py
```

## RPLiDAR-S2_generateAnglePlotLimited.py
[This tool](./RPLiDAR-S2_generateAnglePlotLimited.py) helps to generate visualisation of whether data exists at user-specified angle range.

#### Dependencies

This relies on the `matplotlib`, `numpy`, and `os` library, which can be installed using:

`pip install matplotlib`

`pip install numpy`

`os` is pre-installed as part of the Python Standard Library

#### What this does

- Reads user-provided dump files (generated by SLAMTEC's FrameGrabber app demo).

- Generates INDIVIDUAL visualisation of whether data exists at user-specified angle range, saves to folder.

- Generates COMBINED visualisation of whether data exists at user-specified angle range, saves to folder.

#### How to use

1. Upload dump files to folder, change READ_FOLDER_NAME to the folder name.

2. Change FILENAME_ARR to each of the dumped data file name.

3. Change START_ANGLE to desired starting angle of visualisation.

4. Change END_ANGLE to desired ending angle of visualisation.

5. (Optional) Set DISPLAY to True to display each point cloud before saving if required.

Assuming your dumped files are `control`, `50khz`, and `100khz`, your file structure should look like this.

```
main
| --- folder_with_datafiles
| | --- control
| | --- 50khz
| | --- 100khz
|
| --- RPLiDAR-S2_generateAnglePlotLimited.py
```

After running the program, your file structure will look like this

```
main
| --- folder_with_datafiles
|  | --- control
|  | --- 50khz
|  | --- 100khz
|  |
|  | --- Angle Plot Limited
|  |  | --- control.png
|  |  | --- 50khz.png
|  |  | --- 100khz.png
|  |  | --- Combined.png
|
| --- RPLiDAR-S2_generateAnglePlotLimited.py
```

## RPLiDAR-S2_generateScatterPlotLimited.py
[This tool](./RPLiDAR-S2_generateScatterPlotLimited.py) helps to generate scatter plot of points within user-specified angle range.

#### Dependencies

This relies on the `matplotlib`, `numpy`, and `os` library, which can be installed using:

`pip install matplotlib`

`pip install numpy`

`os` is pre-installed as part of the Python Standard Library

#### What this does

- Reads user-provided dump files (generated by SLAMTEC's FrameGrabber app demo).

- Generates INDIVIDUAL visualisation of whether data exists at user-specified angle range, saves to folder.

- Generates COMBINED visualisation of whether data exists at user-specified angle range, saves to folder.

#### How to use

1. Upload dump files to folder, change READ_FOLDER_NAME to the folder name.

2. Change FILENAME_ARR to each of the dumped data file name.

3. Change START_ANGLE_AFFECTED to desired starting angle of affected range to be shown.

4. Change END_ANGLE_AFFECTED to desired ending angle of affected range to be shown.

5. Change START_ANGLE_NORMAL to desired starting angle of unaffected range to be shown.

6. Change END_ANGLE_NORMAL to desired ending angle of unaffected range to be shown.

7. (Optional )Set DISPLAY to True to display each point cloud before saving if required.

Assuming your dumped files are `control`, `50khz`, and `100khz`, your file structure should look like this.

```
main
| --- folder_with_datafiles
| | --- control
| | --- 50khz
| | --- 100khz
|
| --- RPLiDAR-S2_generateScatterPlotLimited.py
```

After running the program, your file structure will look like this

```
main
| --- folder_with_datafiles
|  | --- control
|  | --- 50khz
|  | --- 100khz
|  |
|  | --- Scatter Plot Limited
|  |  | --- Combined Affected.png
|  |  | --- Combined Normal.png
|
| --- RPLiDAR-S2_generateScatterPlotLimited.py
```


## RPLiDAR-S2_combinedTools.py
[This CLI tool](./RPLiDAR-S2_combinedTools.py) does the job of all my RPLiDAR S2 tools.

#### Dependencies

This relies on the `matplotlib`, `numpy`, `os`, and `argparse` library, which can be installed using:

`pip install matplotlib`

`pip install numpy`

`os` and `argparse` are pre-installed as part of the Python Standard Library

#### What this does

- Reads user-provided dump files (generated by SLAMTEC's FrameGrabber app demo).

- Generates point cloud, saves to folder.

- Generates INDIVIDUAL visualisation of whether data exists at user-specified angle range, saves to folder.

- Generates COMBINED visualisation of whether data exists at user-specified angle range, saves to folder.

- Generates a scatter plot of all points within START_ANGLE_AFFECTED and END_ANGLE_AFFECTED for data files located in folder READ_FOLDER_NAME.

- Generates a scatter plot of all points within START_ANGLE_NORMAL and END_ANGLE_NORMAL for data files located in folder READ_FOLDER_NAME.

#### How to use

1. Upload dump files a folder named FOLDER_NAME

2. Open cmd, run `./RPLiDAR-S2_combinedTools.py "FOLDER_NAME"`

Setting `--filename-arr FILENAME1 FILENAME2 etc` is recrecommended, as it affects the order of parts of some plots.

```
Optional arguments:
  -h, --help            show help message and exit

  --filename-arr FILENAME_ARR [FILENAME_ARR ...]
                        Names of data files.

  -maxd MAX_DISTANCE_SHOWN, --max-distance-shown MAX_DISTANCE_SHOWN
                        Max distance to be shown in Point Cloud (in meters).

  -sa START_ANGLE_AFFECTED, --start-angle-affected START_ANGLE_AFFECTED
                        Start angle for affected values.
                        
  -ea END_ANGLE_AFFECTED, --end-angle-affected END_ANGLE_AFFECTED
                        End angle for affected values.

  -sn START_ANGLE_NORMAL, --start-angle-normal START_ANGLE_NORMAL
                        Start angle for normal values.

  -en END_ANGLE_NORMAL, --end-angle-normal END_ANGLE_NORMAL
                        End angle for normal values.

  -d, --display         If enabled, shows plots before saving.
```

Assuming your dumped files are `control`, `50khz`, and `100khz`, your file structure should look like this.

```
main
| --- folder_with_datafiles
| | --- control
| | --- 50khz
| | --- 100khz
|
| --- RPLiDAR-S2_generateScatterPlotLimited.py
```

After running the program, your file structure will look like this

```
main
| --- folder_with_datafiles
|  | --- control
|  | --- 50khz
|  | --- 100khz
|  |
|  | --- Point Clouds
|  |  | --- control.png
|  |  | --- 50khz.png
|  |  | --- 100khz.png
|  |
|  | --- Angle Plot Limited
|  |  | --- control.png
|  |  | --- 50khz.png
|  |  | --- 100khz.png
|  |  | --- Combined.png
|  |
|  | --- Scatter Plot Limited
|  |  | --- Combined Affected.png
|  |  | --- Combined Normal.png
|
| --- RPLiDAR-S2_generateScatterPlotLimited.py
```

