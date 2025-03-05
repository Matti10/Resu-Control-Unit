#!/bin/bash

# Define the source directory
source_dir="/workspaces/Resu-Control-Unit/src"  # Change this to the directory containing files/folders

# Ensure the source directory exists
if [ ! -d "$source_dir" ]; then
    echo "Error: Source directory does not exist!"
    exit 1
fi

# Loop through all files and directories in the source directory
for item in "$source_dir"/*; do
    # Extract the base name of the file/folder
    name=$(basename "$item")

    # Define the target path in /
    target="/$name"

    # Check if the target already exists
    if [ -e "$target" ] || [ -L "$target" ]; then
        echo "Skipping $name: Target already exists at $target"
    else
        # Create a symbolic link in /
        ln -s "$item" "$target"
        echo "Linked $item -> $target"
    fi
done

echo "All symbolic links created successfully!"
