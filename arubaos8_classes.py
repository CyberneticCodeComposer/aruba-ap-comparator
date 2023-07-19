import requests
import warnings
import logging
import json
import pandas as pd
import variables

class ArubaOS_8:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.session()
        self.uidaruba = self.login()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()
    
    def login(self):
        """Returns the UIDARUBA session cookie."""
        url = f"{self.base_url}/api/login"
        creds = {'username': variables.aos8api['username'],
                'password': variables.aos8api['password']}

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                resp = self.session.post(url, creds, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the request: {e}")
            return None

        return json.loads(resp.text)['_global_result']['UIDARUBA']

    def logout(self):
        """Logs out from the controller."""
        url = f"{self.base_url}/api/logout"

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            resp = self.session.post(url, verify=False)

        #print(json.loads(resp.text)['_global_result']['status_str'])

    def post(self, url, obj):
        """POSTs a JSON object to a URL."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return self.session.post(url, json=obj, verify=False)

    # Other shared methods here...
    def read_db(self):
        '''Gets the AP database'''
        api_page = "/configuration/showcommand"
        show_command = "command=show%20ap%20database%20long"
        
        # Format the URL
        url = f"{self.base_url}{api_page}?{show_command}&UIDARUBA={self.uidaruba}"

        logging.info(f"URL : {url}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = self.session.get(url, verify=False)
            #logging.debug(f"Response : {response.text}")

        return response
    
    def read_db_json(self):
        '''Gets the AP database and returns it as JSON'''
        api_page = "/configuration/showcommand"
        show_command = "command=show%20ap%20database%20long"
        
        # Format the URL
        url = f"{self.base_url}{api_page}?{show_command}&UIDARUBA={self.uidaruba}"
        logging.info(f"URL : {url}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = self.session.get(url, verify=False)
            #logging.debug(f"Response : {response.text}")

        # Convert the response to JSON
        data = response.json()

        # Process the data to only keep the 'Name' and 'Status' fields
        ap_data = data['AP Database']
        for ap in ap_data:
            keys_to_remove = set(ap.keys()) - {'Name', 'Status'}
            for key in keys_to_remove:
                ap.pop(key)

        return data

    def read_db_down(self):
        '''Gets the AP database'''
        api_page = "/configuration/showcommand"
        command = "show ap database long sort-by ap-name status down"
        show_command = "command=" + str(command)

        # Format the URL
        url = f"{self.base_url}{api_page}?{show_command}&UIDARUBA={self.uidaruba}"
        logging.info(f"URL : {url}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = self.session.get(url, verify=False)
            #logging.debug(f"Response : {response.text}")

        return response
    
    def read_db_custom(self, command):
        '''Gets the AP database'''
        api_page = "/configuration/showcommand"
        show_command = "command=" + str(command)

        # Format the URL
        url = f"{self.base_url}{api_page}?{show_command}&UIDARUBA={self.uidaruba}"
        logging.info(f"URL : {url}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = self.session.get(url, verify=False)
            #logging.debug(f"Response : {response.text}")

        return response
    
    def read_lldp_nei(self, ap_name):
        '''Gets the AP LLDP neighbor'''
        api_page = "/configuration/showcommand"
        command = (f"show ap lldp neighbors ap-name {ap_name}")
        show_command = "command=" + str(command)

        # Format the URL
        url = f"{self.base_url}{api_page}?{show_command}&UIDARUBA={self.uidaruba}"

        logging.info(f"URL : {url}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = self.session.get(url, verify=False)
            logging.debug(f"Response : {response.text}")

        return response


class Conductor(ArubaOS_8):
    def __init__(self):
        super().__init__(variables.aos8api['base_url'])
        self.config_path = variables.aos8api['config_path']

    # Add or override methods specific to Conductor here...


class Controller(ArubaOS_8):
    def __init__(self, controller_name):
        base_url = f"https://{controller_name}:4343/v1"  # Adjust the base_url per controller
        super().__init__(base_url)
        self.controller_name = controller_name

    # Add or override methods specific to Controller here...
    def read_bss_table(self):
        api_page = "/configuration/showcommand"
        show_command = "command=show%20ap%20bss-table"

        # Format the URL
        url = f"{self.base_url}{api_page}?{show_command}&UIDARUBA={self.uidaruba}"
        logging.info(f"URL : {url}")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = self.session.get(url, verify=False)
        
        logging.info(f"Response : {response.text}")  # Print the raw response text

        # Save response to a file
        #with open(f"{self.controller_name}_response.txt", "w") as file:
        #    file.write(response.text)

        return response

    def save_bss_table_to_csv(self):
        response = self.read_bss_table()

        # If the response is in JSON format, we extract the "bss", "ess", and "ap name" fields.
        # This part may need to be updated based on the actual response format.
        data = response.json()
        bss_table = data.get('Aruba AP BSS Table', [])

        # Extract the required columns
        df = pd.DataFrame(bss_table)
        df = df[["bss", "ess", "ap name"]]

        # Save to CSV
        df.to_csv(f"{self.controller_name}_bss_table.csv", index=False)
    
    def get_bss_table(self):
        response = self.read_bss_table()

        # If the response is in JSON format, we extract the "bss", "ess", and "ap name" fields.
        # This part may need to be updated based on the actual response format.
        data = response.json()
        bss_table = data.get('Aruba AP BSS Table', [])

        # Extract the required columns
        df = pd.DataFrame(bss_table)
        df = df[["bss", "ess", "ap name"]]

        return df  # Instead of saving to CSV, return the DataFrame
