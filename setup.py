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

from setuptools import setup, find_packages
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, 'requirements.txt')) as f:
    required = f.read().splitlines()

setup(name='radar-robotcar-dataset-sdk',
      version='0.1',
      description='Oxford Radar RobotCar Dataset SDK',
      long_description=open('README.md').read(),
      url='http://github.com/dbarnes/radar-robotcar-dataset-sdk',
      author='Dan Barnes',
      author_email='dbarnes@robots.ox.ac.uk',
      license='Attribution-NonCommercial-ShareAlike 4.0 International',
      packages=find_packages(exclude=['docs']),
      install_requires=required,
      project_urls={
          'Oxford Radar RobotCar Dataset': 'https://ori.ox.ac.uk/datasets/radar-robotcar-dataset',
          'Oxford Radar RobotCar Dataset SDK Source': 'http://github.com/dbarnes/radar-robotcar-dataset-sdk',
          'Oxford Robotics Institute': 'https://ori.ox.ac.uk',
      },
      )
