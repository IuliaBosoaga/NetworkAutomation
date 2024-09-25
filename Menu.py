"""
Module for displaying menu items and executing functions based on user input.
"""
from Switch import Switch
from Router import Router
import json
import logging

logging.basicConfig(level=logging.INFO)

def load_device_data(filename: str) -> dict:
    """
    Loads data from JSON file.
    :param filename: Name of the target file.
    :return: Dictionary containing the device data.
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"File {filename} not found.")
        raise
    except json.JSONDecodeError:
        logging.error(f"Failed to parse {filename}. Ensure it contains valid JSON.")
        raise


def main() -> None:
    """
    Main function responsible for running the main routine.
    Checks if the device to configure exists in the device list.
    :return: None
    """
    try:
        devices = load_device_data('deviceDetails.json')
    except Exception as e:
        print(f"Error loading device data: {e}")
        return

    while True:
        print("""
        Welcome to the Main Menu of the Network Automation Tool!
        
        The following options are available:
        1. Configure a device.
        2. Exit the application.
        """)
        choice = input("Enter your choice: ")
        if choice == '1':
            configure_device(devices)
        elif choice == '2':
            print("Thank you for using the Network Automation Tool!")
            break
        else:
            print("Invalid choice. Please try again.")


def configure_device(devices: dict) -> None:
    """
    Function to configure a device based on user input.
    :param devices: List of available devices.
    :return: None
    """
    target_device_ip = input("Enter the IP of the device you want to configure: ").strip()
    device = next((dev for dev in devices if dev['ip'] == target_device_ip), None)

    if device:
        if "router" in device['type'].lower():
            ConfigMenuRouter(device)
        elif "sw" in device['type'].lower():
            ConfigMenuSwitch(device)
        else:
            print(f"Unknown device type '{device['type']}' for IP: {target_device_ip}")
    else:
        print(f"Device with IP {target_device_ip} not found. Please check the IP or add it to the device list.")


def ConfigMenuRouter(device: dict) -> None:
    """
    Menu with configuration options for a Router.
    :param device: Device data dictionary.
    :return: None
    """
    router_instance = Router(device['name'], device['ip'], device['username'], device['password'], device['privileged_password'])

    while True:
        print("""
        The following configuration options are available for the Router:
        1. Configure HSRP for a VLAN.
        2. Configure a DHCP server.
        3. Set up RIPv2.
        4. Exit to Main Menu.
        """)
        config_choice = input("Enter your choice: ")
        if config_choice == '1':
            router_instance.config_HSRP()
        elif config_choice == '2':
            router_instance.setup_DHCP(device['ip'])
        elif config_choice == '3':
            router_instance.config_RipV2()
        elif config_choice == '4':
            return  # Exit to main menu
        else:
            print("Invalid choice. Please try again.")


def ConfigMenuSwitch(device: dict) -> None:
    """
    Menu with configuration options for a Switch.
    :param device: Device data dictionary.
    :return: None
    """
    switch_instance = Switch(device['name'], device['ip'], device['username'], device['password'], device['privileged_password'])

    while True:
        print("""
        The following configuration options are available for the Switch:
        1. Configure a VLAN.
        2. Configure Security.
        3. Configure STP.
        4. Configure HSRP (for multilayer switches only).
        5. Exit to Main Menu.
        """)
        config_choice = input("Enter your choice: ")
        if config_choice == '1':
            switch_instance.config_Vlan()
        elif config_choice == '2':
            switch_instance.config_Security()
        elif config_choice == '3':
            switch_instance.config_STP()
        elif config_choice == '4':
            if "multilayer" in device['name'].lower():
                switch_instance.config_HSRP()
            else:
                print("This is not a multilayer switch, HSRP configuration is not supported.")
        elif config_choice == '5':
            return  # Exit to main menu
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()