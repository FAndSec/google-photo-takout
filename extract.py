import datetime
import json
import os
import shutil

import PIL
from PIL import Image
from PIL.ExifTags import TAGS

def collect_media_files_from_directory(directory):
    media_files = []
    photo_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic')
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv')

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in photo_extensions or file_extension in video_extensions:
                media_file = os.path.join(root, file)
                json_file = find_json_file(media_file)
                # if we can find the json file, we should update the timestamp
                if json_file:
                    creation_date = get_creation_date_from_json(json_file)
                    if creation_date:
                        print("using json date to reset: ", media_file)
                        set_creation_date(media_file, creation_date)
                else:
                    creation_date = get_content_creation_date_PIL(media_file)
                    if creation_date:
                        print("using content creation date to reset: ", media_file)
                        set_creation_date(media_file, creation_date)

                # if we really can't find date, we will use Google's set date, which might be wrong.
                media_files.append(media_file)

    return media_files


def find_json_file(media_file):
    if '7342' in media_file:
        print(media_file)
    folder = os.path.dirname(media_file)
    json_filename = media_file + '.json'
    json_file = os.path.join(folder, json_filename)
    if os.path.isfile(json_file):
        return json_file

    # Extract the file name without the directory path
    base_file = os.path.basename(media_file)

    # Remove the file extension from the base_file
    file_name, extension = os.path.splitext(base_file)
    file_heic_name = file_name + '.HEIC.json'
    # print(file_heic_name)
    json_file = os.path.join(folder, file_heic_name)
    if os.path.isfile(json_file):
        return json_file

    return None


def get_content_creation_date_PIL(photo_file):
    try:
        # Open the image file using PIL
        image = Image.open(photo_file)

        # Extract the EXIF data
        exif_data = image._getexif()

        # Iterate over the EXIF tags
        for tag_id, value in exif_data.items():
            # Convert the tag ID to the corresponding tag name
            tag_name = TAGS.get(tag_id, tag_id)

            # Check if the tag corresponds to content creation date
            if tag_name == "DateTimeOriginal":
                # Convert the value to a datetime object
                datetime_obj = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

                # Convert the datetime object to epoch timestamp
                epoch_timestamp = datetime_obj.timestamp()

                # Return the epoch timestamp
                return int(epoch_timestamp)
    except (AttributeError, KeyError, IndexError, PIL.UnidentifiedImageError):
        print("Error parsing media: ", photo_file)
        pass

    # Return None if content creation date is not found or an error occurs
    return None


def get_content_created_date(photo_file):
    try:
        # Get the file metadata
        file_stat = os.stat(photo_file)

        # Retrieve the "content created" date from the metadata
        content_created_timestamp = file_stat.st_birthtime

        return content_created_timestamp

    except OSError:
        pass

    # Return None if the "content created" date cannot be retrieved
    return None


def get_creation_date_from_json(json_file):
    with open(json_file) as file:
        data = json.load(file)
        creation_time = data.get('photoTakenTime', {}).get('timestamp')
        if creation_time:
            return int(creation_time)
    return None


def set_creation_date(media_file, creation_date):
    os.utime(media_file, (creation_date, creation_date))


def copy_media_to_destination(media_files, destination_directory):
    # Create the destination folder and any necessary enclosing folders
    os.makedirs(destination_directory, exist_ok=True)

    for media_file in media_files:
        try:
            shutil.move(media_file, destination_directory)
        except Exception as e:
            print(f"An error occurred while moving the file '{media_file}': {str(e)}")




if __name__ == '__main__':
    print("running")
    # Directory with the extracted contents
    extracted_directory = '/path/to/takeouts/Takeout-merged'

    # Destination folder to copy the media files
    destination_directory = '/path/to/takeouts/Take-extract'
    print("next")
    # Collect all files without the "json" suffix from the extracted directory
    media_files = collect_media_files_from_directory(extracted_directory)
    print("then")
    # Copy the media files to the destination folder
    copy_media_to_destination(media_files, destination_directory)
