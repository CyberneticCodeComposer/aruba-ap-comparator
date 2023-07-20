"""
AP Status Comparator

Compares the status of access points before and after maintenance, 
checking for any status changes.

Uses the ArubaOS_8 class to retrieve AP status data from the controller.
Saves the before and after data to JSON files. Loads these files and 
compares the AP status between them, printing any changes.

The key steps are:

1. Connect to the controller and get the latest AP status data
2. If --before: Save the data to before.json
3. If --after: Save the data to after.json 
4. If --compare:
   - Load before data from before.json
   - Load after data from after.json
   - Loop through APs and compare status
   - Print any status changes
   
The AP data is stored in the JSON files like:

{
  "AP Database": [
    {
      "Name": "AP1",
      "Status": "Up 10d:3h:14m:20s"
    },
    ...
  ]
}

The status comparison splits on whitespace to remove the uptime data.

Example Usage:

Get before data:
python ap_comparator.py --before

Get after data:  
python ap_comparator.py --after

Compare before and after:
python ap_comparator.py --compare

Some TODO:

    - Add better logging to track script execution
    - Improve validation of JSON data structure
    - Expand script to support AOS 10
    - Add option to output comparison results to a CSV
    - Add PyTest test cases

"""

import argparse
import json
from arubaos8_classes import ArubaOS_8
import variables
from colorama import Fore, Style
from prettytable import PrettyTable

# Instantiate the ArubaOS_8 class with the base_url from the variables.py file
BEFORE_FILE="before.json"
AFTER_FILE="after.json"

def get_args():
    parser = argparse.ArgumentParser(description='Compare AP database before and after maintenance.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--before', action='store_true', help='Store data before maintenance')
    group.add_argument('--after', action='store_true', help='Store data after maintenance')
    group.add_argument('--compare', action='store_true', help='Compare before and after data sets')
    group.add_argument('--down', action='store_true', help='Only show APs that were up before but are down now')
    return parser.parse_args()

def get_AP_status(aruba_os8):
    data = aruba_os8.read_db_json()
    return data

import os

def store_data(filename, aruba_os8, is_before=False):
    # Ask first before fetching the data
    if is_before and os.path.exists(filename):
        overwrite = input(f"{filename} already exists. Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Operation cancelled.")
            return
    
    data = get_AP_status(aruba_os8)
        
    with open(filename, 'w') as f:
        json.dump(data, f)
    
def load_ap_data(filename):
    """Load AP data from a JSON file"""
    try:
        with open(filename) as f:
            data = json.load(f)
            return data['AP Database']
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"An error occurred while decoding the JSON data in {filename}.")
        return None

def color_status(status):
    """Return colored status"""
    if status == 'Up':
        return f"{Fore.GREEN}{status}{Style.RESET_ALL}"
    elif status == 'Down':
        return f"{Fore.RED}{status}{Style.RESET_ALL}"
    elif status == 'Missing':
        return f"{Fore.MAGENTA}{status}{Style.RESET_ALL}"
    elif status == 'New':
        return f"{Fore.CYAN}{status}{Style.RESET_ALL}"

def get_file_modification_time(filename):
    """Get the last modification time of a file"""
    return os.path.getmtime(filename)

from datetime import datetime, timedelta

def print_file_times(before_time, after_time):
    """Print the modification times and the time difference for two files"""
    
    # Convert timestamps to datetime objects
    before_dt = datetime.fromtimestamp(before_time)
    after_dt = datetime.fromtimestamp(after_time)

    # Format datetime objects as strings
    before_str = before_dt.strftime('%Y-%m-%d %H:%M')
    after_str = after_dt.strftime('%Y-%m-%d %H:%M')

    print(f"Before data loaded from: {Fore.CYAN}{before_str}{Style.RESET_ALL}")
    print(f"After data loaded from: {Fore.CYAN}{after_str}{Style.RESET_ALL}")

    # Calculate time difference and convert it to days, hours, minutes, and seconds
    time_diff = after_dt - before_dt
    days, seconds = time_diff.days, time_diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)

    print(f"Time between before/after: {Fore.YELLOW}{days} days, {hours} hours, {minutes} minutes, {seconds} seconds{Style.RESET_ALL}")


def compare_aps(before, after, only_down=False):
    """Compare AP statuses between before and after"""
    # Create a table with headers
    table = PrettyTable(['AP Name', 'Before Status', 'After Status'])
    down_to_up = 0
    up_to_down = 0
    missing_aps = 0
    new_aps = 0

    # Create a dictionary from the before and after data for easier access
    before_dict = {ap['Name']: ap for ap in before}
    after_dict = {ap['Name']: ap for ap in after}

    total_aps = len(before_dict) + len(after_dict) - len(set(ap['Name'] for ap in before).intersection(after_dict.keys()))

    # Check for APs in the before data that have changed or are missing in the after data
    for before_ap in before:
        before_status = before_ap['Status'].split()[0]
        after_ap = after_dict.get(before_ap['Name'])

        # Check if the AP is missing in the after data
        if after_ap is None:
            missing_aps += 1
            if not only_down:
                table.add_row([before_ap['Name'], color_status(before_status), color_status('Missing')])
        else:
            after_status = after_ap['Status'].split()[0]
            if before_status != after_status:
                # Add a row to the table for each AP with a status change
                if before_status == 'Up' and after_status == 'Down':
                    up_to_down += 1
                    if only_down:
                        table.add_row([before_ap['Name'], color_status(before_status), color_status(after_status)])
                elif before_status == 'Down' and after_status == 'Up':
                    down_to_up += 1
                    if not only_down:
                        table.add_row([before_ap['Name'], color_status(before_status), color_status(after_status)])

    # Check for APs in the after data that are new
    for after_ap in after:
        if before_dict.get(after_ap['Name']) is None:
            new_aps += 1
            if not only_down:
                table.add_row([after_ap['Name'], color_status('Missing'), color_status('New')])

    # Print the table
    print(table)

    # Print the summary
    print(f"Total number of APs: {total_aps}")
    print(f"Total number of status changes: {down_to_up + up_to_down}")
    print(f"Number of APs that changed from Down to Up: {Fore.GREEN}{down_to_up}{Style.RESET_ALL}")
    print(f"Number of APs that changed from Up to Down: {Fore.RED}{up_to_down}{Style.RESET_ALL}")
    print(f"Number of APs Missing: {Fore.MAGENTA}{missing_aps}{Style.RESET_ALL}")
    print(f"Number of New APs: {Fore.CYAN}{new_aps}{Style.RESET_ALL}")



def main():
    aruba_os8 = ArubaOS_8(variables.aos8api['base_url'])
    args = get_args()

    if args.before:
        store_data(BEFORE_FILE, aruba_os8, is_before=True)

    elif args.after:
        store_data(AFTER_FILE, aruba_os8)

    elif args.compare or args.down:
        
        # Read both data sets
        before_data = load_ap_data(BEFORE_FILE)
        after_data = load_ap_data(AFTER_FILE)

        before_time = os.path.getmtime(BEFORE_FILE)
        after_time = os.path.getmtime(AFTER_FILE)

        print_file_times(before_time, after_time)

        compare_aps(before_data, after_data, only_down=args.down)

if __name__ == "__main__":
    main()
