#!/bin/bash

# if setups.sh exist go back to parent folder
if [ -f "setup.sh" ]; then
    cd ..
fi

if [ -f "startpy.sh" ]; then
    # get current directory
    DIR=$(pwd)

    # add execution rights to all .sh files in parent directory
    chmod +x $DIR/*.sh
    # add execution rights to all .py files in parent directory
    chmod +x $DIR/*.py

    # print directory
    echo "Directory: $DIR"

    # add parent to PATH
    # export PATH="$PATH:$DIR"

    # add alias to .bashrc in a new paragraph with title "Custom commands aliases" if does not exist
    if ! grep -q "# custom-commands aliases" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# custom-commands aliases" >> ~/.bashrc
    fi
    # for each sh file in parent directory add alias if does not exist
    for file in $DIR/*.sh; do
        if [ -f "$file" ]; then
            # get file name without extension
            filename=$(basename -- "$file")
            filename="${filename%.*}"
            # check if alias already exists
            if ! grep -q "alias $filename=" ~/.bashrc; then
                echo "alias $filename='$DIR/$filename.sh'" >> ~/.bashrc
            fi
        fi
    done
    # for each py file in parent directory add alias if does not exist
    for file in $DIR/*.py; do
        if [ -f "$file" ]; then
            # get file name without extension
            filename=$(basename -- "$file")
            filename="${filename%.*}"
            # check if alias already exists
            if ! grep -q "alias $filename=" ~/.bashrc; then
                echo "alias $filename='$DIR/$filename.py'" >> ~/.bashrc
            fi
        fi
    done
fi

CONFIG_FILE="$DIR/.todo_config"

echo "Set up path for todo lists"

if [ -f "$CONFIG_FILE" ]; then
    echo "Config file already exists"
    echo "Do you want to change the path for todo lists? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        echo "Enter the path for todo lists, current is $(grep TODO_FILE_PATH "$CONFIG_FILE" | cut -d'=' -f2)"
        read -r path
        echo "TODO_FILE_PATH=$path" > "$CONFIG_FILE"
    fi
else
    echo "Enter the path for todo lists, default is home directory"
    read -r path
    if [ -z "$path" ]; then
        path="$HOME"
    fi
    echo "TODO_FILE_PATH=$path" > "$CONFIG_FILE"
fi

echo "Setup complete"