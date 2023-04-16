#!/bin/bash

# Create a new Python project
mkdir $1
cd $1

# initialize a git repository
git init

# add a .gitignore file
touch .gitignore

# Create a requirements.txt file
touch requirements.txt

# Create a README.md file
touch README.md

# Create a virtual environment
python3 -m venv venv

# Create a .env file
touch .env

# Create a .env.example file
touch .env.example

# copy .gitignore.template to .gitignore
cp ../templates/.gitignore.template .gitignore

# add project name to README.md
echo "# $1" >> README.md

# launch vs code
code .
