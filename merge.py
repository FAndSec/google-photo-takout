import os
import shutil

def copy_files(source_folders, destination_folder):
    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Iterate over the source folders
    for src_folder in source_folders:
        # Iterate over the files in the current source folder
        for filename in os.listdir(src_folder):
            src_file = os.path.join(src_folder, filename)
            dst_file = os.path.join(destination_folder, filename)

            # Copy the file to the destination folder
            if os.path.isfile(src_file):
                shutil.move(src_file, dst_file)

            # If the file is a subfolder, recursively copy its contents
            elif os.path.isdir(src_file):
                copy_files([src_file], dst_file)

# Example usage
destination_folder = '/path/to/takeouts/Takeout-merged'
source_folders = []

for i in range(1, 33):
    folder_path = f'/path/to/takeouts/Takeout-{i}'
    source_folders.append(folder_path)

copy_files(source_folders, destination_folder)
