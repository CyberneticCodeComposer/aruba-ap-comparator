# Aruba AP Status Comparator

Aruba AP Status Comparator is a Python tool that compares the status of Aruba Access Points (APs) before and after maintenance. It fetches AP status data from the controller using the ArubaOS_8 class, stores the data in JSON format, and provides a comparative analysis highlighting any status changes.

## Features

- Fetches and stores AP status data from the Aruba controller in JSON format
- Compares AP status before and after maintenance
- Highlights status changes in a readable format with color coding
- Tracks and displays the time difference between data sets

## Usage

1. To get and store data before maintenance:
   ```
   python ap_comparator.py --before
   ```

2. To get and store data after maintenance:
   ```
   python ap_comparator.py --after
   ```

3. To compare the before and after data:
   ```
   python ap_comparator.py --compare
   ```

## Author

This tool was developed by CyberneticCodeComposer, with assistance from OpenAI's ChatGPT.

## License

This project is licensed under the terms of the MIT license.
