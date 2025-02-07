import requests
import os
import time

def download_picre_varied_images_resume(num_images):
    """
    Downloads multiple versions of the image from pic.re/image, resuming
    from the last downloaded image in the 'picre_varied_images' folder within
    your Documents directory.

    Args:
        num_images (int): The number of different image versions to download
                         (including the resumed ones).
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
            start_index = 1 # if files are named incorrectly, start from 1
    else:
        start_index = 1  # Start from 1 if the folder is empty

    print(f"Resuming download from image_{start_index}.webp")
    for i in range(start_index, start_index + num_images): # Iterate from the start index to start index + requested images
        try:
            response = requests.get(image_url, stream=True)  # stream=True for large files
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

        except requests.exceptions.RequestException as e:
            print(f"Error downloading image {i}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing image {i}: {e}")

        time.sleep(1)  # Wait 1 second to avoid rate limiting
        # You may need to adjust this delay based on pic.re's rate limits.

if __name__ == "__main__":
    while True:
        try:
            count = int(input("Enter the total number of images to download (including resumed ones): "))
            break  # Exit loop if input is valid
        except ValueError:
            print("Invalid input. Please enter an integer.")

    download_picre_varied_images_resume(count)
    print("Download complete.")
