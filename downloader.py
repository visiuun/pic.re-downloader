import requests
import os
import time
import concurrent.futures

def download_image(image_url, output_folder, i):
    """Downloads a single image, handling errors and saving to disk."""
    try:
        response = requests.get(image_url, stream=True, timeout=10)  # timeout added
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Determine the filename from the headers, adding an index to ensure it's unique
        # Force the extension to .webp if it's not found or incorrect
        filename = f"image_{i}.webp"  # Default filename with index and .webp

        if 'content-disposition' in response.headers:
            content_disposition = response.headers['content-disposition']
            filename_start = content_disposition.find("filename=")
            if filename_start != -1:
                filename_from_header = content_disposition[filename_start + len("filename="):].strip('"')
                filename = f"{os.path.splitext(filename_from_header)[0]}_{i}.webp"  # Add unique index and force .webp
            else:
                filename = f"image_{i}.webp" # Default filename if no filename found

        # If the content type contains webp, keep as webp. If not, force webp by changing extension
        content_type = response.headers.get('Content-Type', '')
        if "image/webp" not in content_type.lower():
            filename = f"image_{i}.webp" # Default filename if content type is not webp

        file_path = os.path.join(output_folder, filename)

        with open(file_path, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=8192): # 8KB chunks
                out_file.write(chunk)

        print(f"Downloaded image {i} to {file_path}")
        return True  # Indicate success

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image {i}: {e}")
        return False  # Indicate failure
    except Exception as e:
        print(f"An unexpected error occurred while processing image {i}: {e}")
        return False  # Indicate failure


def download_picre_varied_images_resume(num_images, max_threads=4):  # Added max_threads argument
    """
    Downloads multiple versions of the image from pic.re/image, resuming
    from the last downloaded image in the 'picre_varied_images' folder within
    your Documents directory, using multithreading for faster download speeds.

    Args:
        num_images (int): The number of different image versions to download
                         (including the resumed ones).
        max_threads (int): The maximum number of threads to use for downloading.
    """

    # Get the path to the Documents directory
    documents_path = os.path.expanduser("~/Documents")

    # Create the 'picre_varied_images' folder if it doesn't exist
    output_folder = os.path.join(documents_path, "picre_varied_images")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_url = "https://pic.re/image"  # The single, unchanging URL

    # Determine the starting index by checking existing files
    existing_files = [f for f in os.listdir(output_folder) if f.startswith("image_") and f.endswith(".webp")]
    if existing_files:
        # Extract the numbers from filenames, handle cases where other file types are present
        existing_indices = []
        for filename in existing_files:
            try:
                index = int(filename.split('_')[1].split('.')[0])
                existing_indices.append(index)
            except (IndexError, ValueError):
                print(f"Warning: Could not parse index from existing filename: {filename}")

        if existing_indices:
            start_index = max(existing_indices) + 1
        else:
            start_index = 1  # if files are named incorrectly, start from 1
    else:
        start_index = 1  # Start from 1 if the folder is empty

    print(f"Resuming download from image_{start_index}.webp")

    # Use a thread pool to download images concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(download_image, image_url, output_folder, i)
                   for i in range(start_index, start_index + num_images)]

        # Wait for all downloads to complete (or timeout)
        concurrent.futures.wait(futures)

    print("Download complete.")


if __name__ == "__main__":
    while True:
        try:
            count = int(input("Enter the total number of images to download (including resumed ones): "))
            break  # Exit loop if input is valid
        except ValueError:
            print("Invalid input. Please enter an integer.")

    # Ask for the number of threads to use
    while True:
        try:
            num_threads = int(input("Enter the number of threads to use (default is 4, larger number increases speed but can overwhelm the server): "))
            if num_threads > 0:
                break
            else:
                print("Number of threads must be positive.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    download_picre_varied_images_resume(count, num_threads) # Pass the thread count
    print("Download complete.")
