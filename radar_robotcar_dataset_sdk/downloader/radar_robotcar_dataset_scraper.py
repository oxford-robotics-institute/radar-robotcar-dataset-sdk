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
from absl import app, flags
import requests
from bs4 import BeautifulSoup
import os
from copy import deepcopy

FLAGS = flags.FLAGS
flags.DEFINE_string("dataset_url", "http://ori.ox.ac.uk/datasets/radar-robotcar-dataset",
                    "Oxford Radar RobotCar Dataset url")


class DatasetScraper:
    def __init__(self, base_url=None):
        base_url = base_url if base_url is not None else FLAGS.dataset_url
        self.base_url = requests.get(base_url).url  # resolve redirects
        self.datesets_url = f"{self.base_url}/datasets"
        self.downloads_url = f"{self.base_url}/downloads"

    def get_dataset_list(self):
        response = requests.get(self.datesets_url)
        soup = BeautifulSoup(response.text, "html.parser")
        table_rows = soup.findAll('tr')
        datasets = [tr['href'] for tr in table_rows]
        datasets = [os.path.basename(d) for d in datasets]
        return datasets

    def get_dataset_info(self, dataset):
        response = requests.get(f"{self.datesets_url}/{dataset}")
        soup = BeautifulSoup(response.text, "html.parser")
        table_rows = soup.findAll('tr')
        dataset_info = {}
        for tr in table_rows:
            td = tr.find('td')
            sensor_info_lines = td.get_text().strip().splitlines()[:-1]
            sensor_info = {}
            for line in sensor_info_lines[1:]:
                k, v = line.split(": ")
                sensor_info[k] = v
            download = td.find('a')
            if "available soon" in download.text.lower():
                sensor_info['Download'] = "Available Soon"
            else:
                sensor_info['Download'] = download['href']
            dataset_info[sensor_info_lines[0].strip()] = deepcopy(sensor_info)

        return dataset_info

    def get_sample_dataset_list(self):
        response = requests.get(self.downloads_url)
        soup = BeautifulSoup(response.text, "html.parser")
        sample_datasets_div = soup.find("div", {"id": "sample_datasets"})
        sample_datasets_elements = sample_datasets_div.find_all('li')
        sample_datasets = dict()
        for sample_datasets_element in sample_datasets_elements:
            name = sample_datasets_element.next.split('(')[0].split(' ')[0].strip()
            link = sample_datasets_element.find('a')['href']
            size = sample_datasets_element.next.split('(')[1].split(')')[0]
            sample_datasets[name] = {'Size': size, 'Download': link}
        return sample_datasets


def main(unused_args):
    dataset_scraper = DatasetScraper()
    print("\nIndividual Dataset Downloads")
    dataset_list = dataset_scraper.get_dataset_list()
    for dataset in dataset_list:
        print(dataset)
        dataset_info = dataset_scraper.get_dataset_info(dataset_list[0])
        for sensor, info in dataset_info.items():
            print(f"  {sensor} - {info}")

    print("\nSample Dataset Downloads")
    sample_datasets = dataset_scraper.get_sample_dataset_list()
    for sample_dataset_name, sample_dataset_link in sample_datasets.items():
        print(f"  {sample_dataset_name} - {sample_dataset_link}")


if __name__ == '__main__':
    app.run(main)
