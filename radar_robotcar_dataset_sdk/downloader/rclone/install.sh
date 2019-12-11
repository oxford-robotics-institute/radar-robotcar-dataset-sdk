#!/usr/bin/env bash

# Notes:
# Source  - https://rclone.org/install.sh
# Data    - 11/12/2019
# License - MIT (`COPYING` file sourced from https://github.com/rclone/rclone/blob/master/COPYING)
# Reason  - Patched install script contents to fixed version ensure reproducible usage
# Changes - rclone binary installed to `install_dir` - arg #1
#         - use rclone version `version` - arg #2
#         - do not copy any manual files
# Usage   - `bash rclone_isntall.sh install_dir version`
# Example - `bash rclone_isntall.sh /data/download_folder v1.50.2`
#

# error codes
# 0 - exited without problems
# 1 - parameters not supported were used or some unexpected error occurred
# 2 - OS not supported by this script
# 3 - installed version of rclone is already at requested version
# 4 - supported unzip tools are not available

set -e

#when adding a tool to the list make sure to also add it's corresponding command further in the script
unzip_tools_list=('unzip' '7z' 'busybox')

usage() { echo "Usage: curl https://rclone.org/install.sh | bash install_dir version" 1>&2; exit 1; }

if [ "$#" != "2" ]; then
    echo "Illegal number of parameters"
    usage
fi

# parse flags
INSTALL_DIR="$1"
INSTALL_VERSION="$2"

#create tmp directory and move to it with macOS compatibility fallback
tmp_dir=`mktemp -d 2>/dev/null || mktemp -d -t 'rclone-install.XXXXXXXXXX'`; cd $tmp_dir

#make sure unzip tool is available and choose one to work with
set +e
for tool in ${unzip_tools_list[*]}; do
    trash=`hash $tool 2>>errors`
    if [ "$?" -eq 0 ]; then
        unzip_tool="$tool"
        break
    fi
done
set -e

# exit if no unzip tools available
if [ -z "${unzip_tool}" ]; then
    printf "\nNone of the supported tools for extracting zip archives (${unzip_tools_list[*]}) were found. "
    printf "Please install one of them and try again.\n\n"
    exit 4
fi

# Make sure we don't create a root owned .config/rclone directory #2127
export XDG_CONFIG_HOME=config


#make sure install dir in on path and check installed version of rclone to determine if update is necessary
version=`PATH=${INSTALL_DIR}:${PATH} && rclone --version 2>>errors | head -n 1 | cut -d' ' -f2`

if [ "$version" = "$INSTALL_VERSION" ]; then
    printf "\nThe required version of rclone ${version} is already installed.\n\n"
    exit 3
fi



#detect the platform
OS="`uname`"
case $OS in
  Linux)
    OS='linux'
    ;;
  FreeBSD)
    OS='freebsd'
    ;;
  NetBSD)
    OS='netbsd'
    ;;
  OpenBSD)
    OS='openbsd'
    ;;
  Darwin)
    OS='osx'
    ;;
  SunOS)
    OS='solaris'
    echo 'OS not supported'
    exit 2
    ;;
  *)
    echo 'OS not supported'
    exit 2
    ;;
esac

OS_type="`uname -m`"
case $OS_type in
  x86_64|amd64)
    OS_type='amd64'
    ;;
  i?86|x86)
    OS_type='386'
    ;;
  arm*)
    OS_type='arm'
    ;;
  aarch64)
    OS_type='arm64'
    ;;
  *)
    echo 'OS type not supported'
    exit 2
    ;;
esac


#download and unzip
download_link="https://downloads.rclone.org/$INSTALL_VERSION/rclone-$INSTALL_VERSION-$OS-$OS_type.zip"
rclone_zip="rclone-$INSTALL_VERSION-$OS-$OS_type.zip"

curl -O $download_link
unzip_dir="tmp_unzip_dir_for_rclone"
# there should be an entry in this switch for each element of unzip_tools_list
case $unzip_tool in
  'unzip')
    unzip -a $rclone_zip -d $unzip_dir
    ;;
  '7z')
    7z x $rclone_zip -o$unzip_dir
    ;;
  'busybox')
    mkdir -p $unzip_dir
    busybox unzip $rclone_zip -d $unzip_dir
    ;;
esac

cd $unzip_dir/*


#mounting rclone to environment

case $OS in
  'linux')
    #binary
    cp rclone ${INSTALL_DIR}/rclone.new
    chmod 755 ${INSTALL_DIR}/rclone.new
    chown ${USER}: ${INSTALL_DIR}/rclone.new
    mv ${INSTALL_DIR}/rclone.new ${INSTALL_DIR}/rclone
    #manuals
    #if ! [ -x "$(command -v mandb)" ]; then
    #    echo 'mandb not found. The rclone man docs will not be installed.'
    #else
    #    mkdir -p ${INSTALL_DIR}/share/man/man1
    #    cp rclone.1 ${INSTALL_DIR}/share/man/man1/
    #    mandb
    #fi
    ;;
  'freebsd'|'openbsd'|'netbsd')
    #bin
    cp rclone ${INSTALL_DIR}/rclone.new
    chown ${USER}: ${INSTALL_DIR}/rclone.new
    mv ${INSTALL_DIR}/rclone.new ${INSTALL_DIR}/rclone
    #man
    #mkdir -p ${INSTALL_DIR}/man/man1
    #cp rclone.1 ${INSTALL_DIR}/man/man1/
    #makewhatis
    ;;
  'osx')
    #binary
    mkdir -p ${INSTALL_DIR}
    cp rclone ${INSTALL_DIR}/rclone.new
    mv ${INSTALL_DIR}/rclone.new ${INSTALL_DIR}/rclone
    #manual
    #mkdir -p ${INSTALL_DIR}/share/man/man1
    #cp rclone.1 ${INSTALL_DIR}/share/man/man1/
    ;;
  *)
    echo 'OS not supported'
    exit 2
esac


#update version variable post install
version=`rclone --version 2>>errors | head -n 1`

printf "\n${version} has successfully installed."
printf '\nNow run "rclone config" for setup. Check https://rclone.org/docs/ for more details.\n\n'
exit 0