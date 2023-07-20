# AP Status Comparator

This script compares the status of wireless access points before and after maintenance, checking for any status changes. 

It utilizes the ArubaOS_8 API to retrieve AP status data from an Aruba controller. The before and after data is saved to JSON files, loaded back in, and compared. Any status changes are printed in a formatted table.

## Usage

The script accepts 3 arguments:

```
python ap_comparator.py --before
python ap_comparator.py --after 
python ap_comparator.py --compare
```

* `--before` - Get latest data from controller and save to `before.json`
* `--after` - Get latest data from controller and save to `after.json`
* `--compare` - Load `before.json` and `after.json`, compare, and print results

## Examples

Get before status data:

```
python ap_comparator.py --before
```

Get after status data:

``` 
python ap_comparator.py --after
```

Compare before and after data:

```
python ap_comparator.py --compare
```

## Output

The script prints a summary of any AP status changes in an easy to read table with colored formatting. 

For example:

![Screenshot](Screenshot.png)

## Requirements

- Python 3
- ArubaOS 8 API access
- colorama
- prettytable

