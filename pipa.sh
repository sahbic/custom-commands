#!/bin/bash

# This scripts pip install $1, gets the version installed from pip list, and adds it to requirements.txt

# get this script directory
DIR=$(dirname "$0")

# get the name of the package
PACKAGE=$1

# install the package
pip install $PACKAGE

# get the version of the package
VERSION=$(pip list | grep $PACKAGE | awk '{print $2}')

# print the package and version
echo "Installing $PACKAGE==$VERSION"

# add the package and version to requirements.txt
echo "$PACKAGE==$VERSION" >> requirements.txt