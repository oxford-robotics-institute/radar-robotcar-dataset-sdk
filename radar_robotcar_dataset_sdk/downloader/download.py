################################################################################
#
# Copyright (c) 2019 University of Oxford
# Authors:
#  Dan Barnes (dbarnes@robots.ox.ac.uk)
#
# This work is licensed under the Creative Commons
# Attribution-NonCommercial-ShareAlike 4.0 International License.
# To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to
# Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#
###############################################################################

from __future__ import division, print_function, absolute_import
from absl import app, logging, flags
import click
import zipfile
import os
from google_drive_downloader import GoogleDriveDownloader as gdd

from radar_robotcar_dataset_sdk.downloader.radar_robotcar_dataset_scraper import DatasetScraper
from radar_robotcar_dataset_sdk.downloader.gdrive_handler import GDriveHandler

FLAGS = flags.FLAGS

flags.DEFINE_string("download_folder", None, "Download folder (otherwise just list matching downloads). "
                                             "Please note on Linux this folder cannot be in `/tmp` as some distros "
                                             "cannot run executables there.")
flags.DEFINE_string("sensors", None, "Comma separated list of sensors to download (None is all)")
flags.DEFINE_string("datasets", None, "Comma separated list of datasets to download (None is all)")
flags.DEFINE_string("sample_dataset", None, "Sample dataset to download (one of `Tiny|Small|Medium|Large`). "
                                            "If provided --datasets and --sensors are ignored.")
flags.DEFINE_bool("verbose", False, "Verbosely print sensor information")


def human_readable_size_to_GB(human_readable_size_str):
    size, multiplier = human_readable_size_str.strip().split()
    size = float(size)
    multiplier = multiplier.upper()
    if multiplier == "GB":
        pass
    elif multiplier == "MB":
        size /= 1024
    elif multiplier == "KB":
        size /= 1024 ** 2
    elif multiplier == "B":
        size /= 1024 ** 3
    return size


def main(unused_args):
    print("\nOxford Radar RobotCar Dataset Downloader")
    print("==========================================================")

    print("Any issues please contact: radarrobotcardataset@robots.ox.ac.uk")
    print(f"Scraping dataset info from: {FLAGS.dataset_url}")

    dataset_scraper = DatasetScraper()

    sample_datasets = dataset_scraper.get_sample_dataset_list()
    datasets_raw = dataset_scraper.get_dataset_list()
    sensors_raw = list(dataset_scraper.get_dataset_info(datasets_raw[0]).keys())

    print("\nAvaiable Sample Datasets:")
    print("==========================================================")
    print("\n".join(sample_datasets))

    if FLAGS.sample_dataset is not None:
        if FLAGS.sample_dataset not in sample_datasets:
            print(f"\nCould not find sample dataset: '{FLAGS.sample_dataset}'. "
                  f"Please check it is one of the below sample dataset keys")
            print("==========================================================")
            print("\n".join(sample_datasets))
        else:
            sample_dataset_download = sample_datasets[FLAGS.sample_dataset]
            print(f"\nMatched Sample Dataset")
            print("==========================================================")
            print(f"Sample dataset to download: {FLAGS.sample_dataset}")
            print(f"Total download size (before unpacking): {sample_dataset_download['Size']}\n")
            if FLAGS.download_folder is not None:
                print("Are you sure you want to download the above files and unpack into:")
                print(FLAGS.download_folder)
                if not click.confirm("\nDo you wish to continue?", False):
                    print("Download cancelled...")
                    return
                print(f"Downloading Sample Dataset: {FLAGS.sample_dataset} - {sample_dataset_download['Size']} - "
                      f"{sample_dataset_download['Download']}")
                file_id = os.path.basename(sample_dataset_download['Download'])
                # The sample datasets are public so we do not use the authenticated GDrive
                download_path = FLAGS.download_folder + \
                                f"/oxford_radar_robotcar_dataset_sample_{FLAGS.sample_dataset.lower()}.zip"
                gdd.download_file_from_google_drive(file_id, download_path, overwrite=True, unzip=True, showsize=True)
                print(f"\nDownload completed into: {FLAGS.download_folder}\n")
            else:
                print("--download_folder is missing. Returning.")
        return

    print("\nAvaiable Datasets:")
    print("==========================================================")
    print("\n".join(datasets_raw))

    if FLAGS.datasets is None:
        datasets = datasets_raw
    else:
        datasets = FLAGS.datasets.split(',')
        for dataset in datasets:
            if dataset not in datasets_raw:
                print(f"\nCould not find dataset: '{dataset}'. Please check it is one of the below datasets")
                print("==========================================================")
                print("\n".join(datasets_raw))
                return

        print("")
        print(f"\nDatasets Matching Filter --datasets `{FLAGS.datasets}`:")
        print("==========================================================")
        print("\n".join(datasets))
        print("")

    print("\nAvaiable Sensors:")
    print("==========================================================")
    print("\n".join(sensors_raw))

    if FLAGS.sensors is None:
        sensors = sensors_raw
    else:
        sensors = FLAGS.sensors.split(',')
        for sensor in sensors:
            if sensor not in sensors_raw:
                print(f"\nCould not find sensor: '{sensor}'. Please check it is one of the below sensors")
                print("==========================================================")
                print("\n".join(sensors_raw))
                return

        print(f"\nSensors Matching Filter --sensors `{FLAGS.sensors}`:")
        print("==========================================================")
        print("\n".join(sensors))
        print("")

    print(f"\nFinding Matching Files...")
    print("==========================================================" * 4)
    print(f"{'Match No':8} : {'Dataset':48} - {'Sensor':50} - {'Download Size':17} - {'Download Link':100}")
    downloads = []
    total_size = 0.
    for di, dataset in enumerate(datasets):
        dataset_info = dataset_scraper.get_dataset_info(dataset)
        dataset_info = {k: dataset_info[k] for k in sensors}
        for si, (k, v) in enumerate(dataset_info.items()):
            downloads.append([dataset, k, v['Size'], v['Download']])
            if len(v['Size']) > 0:
                total_size += human_readable_size_to_GB(v['Size'])
            print(f"{len(downloads):>8} : {dataset:48} - {k:50} - {v['Size']:17} - {v['Download']:100}")
            if FLAGS.verbose:
                print(f"{'Verbose':>8} : {v}")
        print("")

    if FLAGS.download_folder is not None:
        print(f"Number of files to download: {len(downloads)}")
        print(f"Total download size (before unpacking): {total_size:.2f} GB\n")

        print("Are you sure you want to download the above files and unpack into:")
        print(FLAGS.download_folder)
        if not click.confirm("\nDo you wish to continue?", False):
            print("Download cancelled...")
            return

        print("")
        gdrive_handler = GDriveHandler(FLAGS.download_folder)
        for di, downld in enumerate(downloads):
            print(
                f"Downloading {di:4} / {len(downloads):4} : {downld[0]:48} - {downld[1]:25} - {downld[2]:17} - "
                f"{downld[3]:100}")
            if "available soon" in downld[3].lower():
                print(f"Sorry this download isn't available yet, but it will be soon. Skipping...")
            else:
                downloaded_zip_file_path = gdrive_handler.download(os.path.basename(downld[3]))

                print(f"Extracting into: {FLAGS.download_folder} ...")
                downloaded_zip_file = zipfile.ZipFile(downloaded_zip_file_path, allowZip64=True)
                downloaded_zip_file.extractall(FLAGS.download_folder)
                print(f"Deleting Zip File {downloaded_zip_file_path} ...")
                os.remove(downloaded_zip_file_path)

        print(f"\nDownload completed into: {FLAGS.download_folder}\n")


if __name__ == '__main__':
    logging.set_verbosity(-1)
    app.run(main)
