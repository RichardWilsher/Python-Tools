# program to look through a directory and compare images looking for duplicated images
import cv2
import numpy as np
import os
import shutil
import time

start_time = time.time()  # Record the start time

basedir = r'e:\temp\Processing'  # Set the base directory

def get_image_list():
    """
    Get a list of images in the base directory
    :return: List of image filenames
    """
    images = []
    
    for path in os.listdir(basedir):
        if os.path.isfile(os.path.join(basedir, path)):
            images.append(path)
    return images

def is_similar(image1, image2):
    """
    Check if two images are similar
    :param image1: First image
    :param image2: Second image
    :return: True if images are similar, False otherwise
    """
    return image1.shape == image2.shape and not(np.bitwise_xor(image1,image2).any())

images = get_image_list()  # Get the initial list of images

unique_count = 0  # Initialize count of unique images
duplicate_count = 0  # Initialize count of duplicate images

while len(images) > 1:
    os.system('cls' if os.name == 'nt' else 'clear') # clear the screen
    print(str(len(images)-2) + " Remaining...") # display the number of images to be processed 

    duplicates = []  # Initialize list of duplicate images
    first_image_index = 0  # Start from the first image index

    if len(images) > 1:  # Check if there are at least 2 images
        image1_path = os.path.join(basedir, images[first_image_index])  # Get the path of the first image
        image1 = cv2.imread(image1_path, cv2.IMREAD_UNCHANGED)  # Read the first image with IMREAD_UNCHANGED flag
        size1 = os.path.getsize(image1_path)  # Get the size of the first image

        for second_image_index in range(first_image_index + 1, len(images)):
            image2_path = os.path.join(basedir, images[second_image_index])  # Get the path of the second image
            size2 = os.path.getsize(image2_path)  # Get the size of the second image

            if size1 == size2:  # Check if sizes are equal
                image2 = cv2.imread(image2_path, cv2.IMREAD_UNCHANGED)  # Read the second image with IMREAD_UNCHANGED flag
                if is_similar(image1, image2):  # Check if images are similar
                    duplicates.append(images[second_image_index])  # Add the second image to duplicates

        if duplicates:  # Check if there are any duplicates
            for duplicate in duplicates:
                shutil.move(os.path.join(basedir, duplicate), os.path.join(basedir, 'dupe'))  # Move duplicate images to 'dupe' directory
                duplicate_count += 1  # Increment duplicate count
        shutil.move(image1_path, os.path.join(basedir, 'images'))  # Move the first image to 'images' directory
        unique_count += 1  # Increment unique count

    images = get_image_list()  # Update images for the next iteration

if len(images) == 1:  # Check if there is only one image left
    shutil.move(os.path.join(basedir, images[0]), os.path.join(basedir, 'images'))  # Move the remaining image to 'images' directory
    unique_count += 1  # Increment unique count

os.system('cls' if os.name == 'nt' else 'clear') # clear the screen
print("Completed in %.2f seconds" % (time.time() - start_time))  # Print the time taken to complete
print("Unique images: " + str(unique_count))  # Print the count of unique images
print("Duplicate images: " + str(duplicate_count))  # Print the count of duplicate images