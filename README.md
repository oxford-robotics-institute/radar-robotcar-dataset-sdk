# Oxford Radar RobotCar Dataset SDK

![](docs/dataset-overview-overlay.png)

This repo provides additional python helpers for the Oxford Radar RobotCar Dataset, A Radar Extension to the Oxford RobotCar Dataset (currently just a downloader utility).

Matlab and Python parsers for all the data are included in the original [**Oxford RobotCar Dataset SDK**](https://github.com/ori-mrg/robotcar-dataset-sdk)


** Please Read **
--------------
Although the automatic downloader script and other code has been tested extensively we accept no liability for use of the code.
If you have any concerns please review the source code before using.

Using [**rclone**](https://github.com/rclone/rclone) (the binary used to download the dataset files) we target download files by filename rather than id.
If you have other files shared with you in Google Drive that match our dataset filenames you may encounter unintended errors.
However as we use long filenames such as `2019-01-15-14-24-38-radar-oxford-10k_Bumblebee_XB3_Visual_Odometry` we believe this is unlikely and additionally, we use read only permission for additional safety.


Modules
-----------
All modules are contained in the base module `radar_robotcar_dataset_sdk`

`downloader`: Downloader script to automate and simplify downloading the Oxford Radar RobotCar Dataset


Obtaining Data
--------------
To obtain the data, please first register on the [dataset website](http://ori.ox.ac.uk/datasets/radar-robotcar-dataset) to enable downloads for your Google account. Data can be downloaded manually via the website or using the script in this repository. 

Downloads are separated into individual zip files for each sensor, for each traversal. It is recommended that you extract all tar files to the same directory - this will leave all the data in a sensible heirarchical directory structure. 


Please note the automated download using [**rclone**](https://github.com/rclone/rclone) is **completely optional** and you are free to download the files manually through your browser at [ori.ox.ac.uk/datasets/radar-robotcar-dataset/datasets](https://ori.ox.ac.uk/datasets/radar-robotcar-dataset/datasets).

Installation 
--------------

```bash
# Either clone the package manually and add it to your PYTHONPATH or install it using:
pip install git+https://git@github.com/dbarnes/radar-robotcar-dataset-sdk.git
```

Data Download
--------------
The example code below assumes you have installed this repo as a package as described above

```bash
# Downloader help
python -m radar_robotcar_dataset_sdk.downloader.download --help

# Which will print
#  --datasets: Comma separated list of datasets to download (None is all)
#  --download_folder: Download folder (otherwise just list matching downloads). Please note on Linux this folder 
#       cannot be in `/tmp` as some distros cannot run executables there.
#  --sample_dataset: Sample dataset to download (one of `Tiny|Small|Medium|Large`).
#    If provided --datasets and --sensors are ignored.
#  --sensors: Comma separated list of sensors to download (None is all)
#  --[no]verbose: Verbosely print sensor information
#    (default: 'false')

# List, but dont download, all sample datasets, datasets and sensor downloads (no arguments)
python -m radar_robotcar_dataset_sdk.downloader.download

# Download the `Small` sample dataset
python -m radar_robotcar_dataset_sdk.downloader.download --sample_dataset Small \
	--download_folder /data/oxford-radar-robotcar-dataset

# Download Radar and GPS/INS Data from two Datasets
python -m radar_robotcar_dataset_sdk.downloader.download \
	--datasets="2019-01-16-11-53-11-radar-oxford-10k,2019-01-16-13-09-37-radar-oxford-10k" \
	--sensors="Navtech CTS350-X Radar,NovAtel GPS / INS" \
	--download_folder /data/oxford-radar-robotcar-dataset

# Will will prompt for a confirmation as shown below. Simply confirm to download data
# Finding Matching Files...
# ========================================================================================================================================================================================================================================
# Match No : Dataset                                          - Sensor                                             - Download Size     - Download Link
#        1 : 2019-01-16-11-53-11-radar-oxford-10k             - Navtech CTS350-X Radar                             - 3.3 GB            - https://drive.google.com/file/d/1bQviDEkU20uq-xGeHrciaA5YeOr1-uyW
#        2 : 2019-01-16-11-53-11-radar-oxford-10k             - NovAtel GPS / INS                                  - 16.4 MB           - https://drive.google.com/file/d/1b1wNBtSumoqUeYxAMCwcjEKHPOZpn36h
# 
#        3 : 2019-01-16-13-09-37-radar-oxford-10k             - Navtech CTS350-X Radar                             - 3.3 GB            - https://drive.google.com/file/d/17IP4JagskFe2q_yIky-wgBjUUYYtMXxl
#        4 : 2019-01-16-13-09-37-radar-oxford-10k             - NovAtel GPS / INS                                  - 16.5 MB           - https://drive.google.com/file/d/1vVlNaCqY2jwohm8k_oCOWyQKyB1jR8cq
# 
# Number of files to download: 4
# Total download size (before unpacking): 6.63 GB
# 
# Are you sure you want to download the above files and unpack to:
# /data/oxford-radar-robotcar-dataset
# 
# Do you wish to continue? [y/N]:
# 

# Download ALL datasets and ALL sensors (do not specify datasets or sensors)
python -m radar_robotcar_dataset_sdk.downloader.download \
	--download_folder /data/oxford-radar-robotcar-dataset
	
```
### Google Account Verification

We provide authorised downloads via Google Drive for each registered user.
To automatically handle this we use rclone which can be found at: `https://github.com/rclone/rclone`.
This binary is automatically downloaded and run as part of the download script.
To use this binary you will need to give permission for the binary to use your credentials.
When prompted simply follow the instructions (as shown below) by:

- Going to the url in your browser (opened automatically in a browser if run locally)
- Selecting the Google Account which has been given download access
- Pasting the verification code back into the prompt


```

====================================================================================================
rclone config not authorised for downloads: /tmp/radar_robotcar_dataset_test_download/rclone_rrcd.conf
Authorisation needed. Please follow the rclone instructions to generate a read only Google Drive token
Please use the Google Drive account you signed up with and were authorised for at: https://ori.ox.ac.uk/datasets/radar-robotcar-dataset/registration
====================================================================================================

Use auto config?
 * Say Y if not sure
 * Say N if you are working on a remote or headless machine
Auto confirm is set: answering No, override by setting config parameter config_is_local=true
If your browser doesn't open automatically go to the following link: https://accounts.google.com/o/oauth2/auth?...
Log in and authorize rclone for access
Enter verification code> <ENTER_CODE_HERE>

rclone authorised sucessfully

```


Details
-----------

Further details about the Oxford Radar RobotCar Dataset Dataset and associated projects can be found here: 
<br> [[Website]](https://ori.ox.ac.uk/datasets/radar-robotcar-dataset) &nbsp;&nbsp;[[Paper]](https://arxiv.org/pdf/1909.01300)

The dataset follows the same route and uses the same RobotCar platform as the original Oxford RobotCar Dataset, details of which can be found at:
<br> [[Website]](https://robotcar-dataset.robots.ox.ac.uk) &nbsp;&nbsp;[[Paper]](https://robotcar-dataset.robots.ox.ac.uk/images/robotcar_ijrr.pdf) &nbsp;&nbsp;[[SDK]](https://github.com/ori-drs/robotcar-dataset-sdk)


Citation
--------------
If you use this dataset in your research, please cite both of the following papers:

```bibtex
@article{RadarRobotCarDatasetArXiv,
  author = {Dan Barnes and Matthew Gadd and Paul Murcutt and Paul Newman and Ingmar Posner},
  title = {The Oxford Radar RobotCar Dataset: A Radar Extension to the Oxford RobotCar Dataset},
  journal = {arXiv preprint arXiv: 1909.01300},
  url = {https://arxiv.org/pdf/1909.01300},
  pdf = {https://arxiv.org/pdf/1909.01300.pdf},
  year = {2019}
}
```
```bibtex
@article{RobotCarDatasetIJRR, 
  Author = {Will Maddern and Geoff Pascoe and Chris Linegar and Paul Newman}, 
  Title = {{1 Year, 1000km: The Oxford RobotCar Dataset}}, 
  Journal = {The International Journal of Robotics Research (IJRR)}, 
  Volume = {36}, 
  Number = {1}, 
  Pages = {3-15}, 
  Year = {2017}, 
  doi = {10.1177/0278364916679498}, 
  URL = {http://dx.doi.org/10.1177/0278364916679498}, 
  eprint = {http://ijr.sagepub.com/content/early/2016/11/28/0278364916679498.full.pdf+html}, 
  Pdf = {https://robotcar-dataset.robots.ox.ac.uk/images/robotcar_ijrr.pdf}
}
```

License
--------------
This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-nc-sa/4.0) and is intended for non-commercial academic use. If you are interested in using the dataset for commercial purposes please contact us.
