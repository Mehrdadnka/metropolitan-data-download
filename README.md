# Iranian Pottery Dataset Collector Metropolitan-Dataset-Api

A Python-based tool designed to automate the process of collecting, classifying, and storing high-quality images and metadata of Iranian pottery artifacts from The Metropolitan Museum of Art (MET) public API.

## Purpose

This tool was developed as part of a research project on the classification of ancient pottery from Iran for use in machine learning applications, including historical period classification and digital heritage preservation.

## Features

- Downloads images and metadata from the MET Museum Collection API.
- Classifies artifacts into:
  - **Pre-Islamic periods** (e.g., Elam, Achaemenid, Sassanian)
  - **Islamic periods** (e.g., Safavid, Seljuk, Qajar)
- Automatically structures data into period-based folders.
- Exports metadata in both JSON and CSV formats.
- Includes error handling, retries, and progress bars.
- Lightweight and fully configurable.

## Configuration

The main settings are defined in the `CONFIG` dictionary inside the script:

- `dataset_path`: Destination folder
- `timeout`: HTTP request timeout
- `retries`: Number of retries per download
- `max_images`: Maximum number of images to download
- `historical_periods`: Keywords for period classification
- `user_agents`: Random User-Agent selection for API requests

## Usage

1. Install required libraries:
    ```bash
    pip install requests tqdm
    ```

2. Run the script:
    ```bash
    python iran_pottery_downloader.py
    ```

3. Results:
    - Images saved in `./iran_pottery_dataset/images/`
    - Metadata available in:
        - `iran_pottery_metadata.json`
        - `iran_pottery_metadata.csv`

## Limitations

- Depends on the availability and accuracy of the MET API.
- Classification is keyword-based; false positives are possible.
- Designed for initial dataset preparation; manual curation is recommended.

## Author

**مهرداد (Mehrdad)**  
Master's Thesis Project - [Your University Name Here]  
Email: [Your Email]  
GitHub: [Your GitHub Profile URL]

## License

This project is released under the MIT License.
