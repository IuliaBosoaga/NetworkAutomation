"""
Module responsible for handling common functionality between different device types, such as HSRP configuration.
"""
import logging
from Connection import DeviceConnection


class Device:
    def __init__(self, name: str, ip: str, username: str, password: str, priv_exec_pass: str):
        """
        Constructor for Device class.

        :param name: The name of the device (e.g., Router, Switch).
        :param ip: The IP address of the device.
        :param username: The username for the device.
        :param password: The password for the device.
        :param priv_exec_pass: The password for privileged exec mode.
        """
        self.name = name
        self.ip = ip
        self.username = username
        self.password = password
        self.priv_exec_pass = priv_exec_pass
        self.connection = DeviceConnection(ip, username, password)

    def config_HSRP(self) -> None:
        """
        Method for configuring HSRP (Hot Standby Router Protocol), common for both routers and switches.
        This method establishes a connection, prompts for HSRP settings, sends the configuration commands,
        and then closes the connection.

        :return: None
        """
        try:
            logging.info(f"Starting HSRP configuration on device {self.name} ({self.ip})")
            self.connection.connect(self.priv_exec_pass)

            # Gather required HSRP information from the user
            interface = input("Enter the ID of the interface (e.g., Gi0/1): ").strip()
            standby_id = input("Enter the ID of the standby group (e.g., 1): ").strip()
            vrouter_ip = input("Enter the IP address of the Virtual Router: ").strip()

            # Default the priority if not provided or invalid
            priority = input("Enter the priority of the physical interface (default 100): ").strip() or "100"

            try:
                priority = int(priority)
            except ValueError:
                logging.warning(f"Invalid priority provided. Defaulting to 100.")
                priority = 100

            # Construct the HSRP configuration commands
            hsrp_config_commands = (
                f"interface {interface}\n"
                f"standby {standby_id} ip {vrouter_ip}\n"
                f"standby {standby_id} priority {priority}\n"
                f"standby {standby_id} preempt\n"
            )

            # Send the HSRP configuration to the device
            stdout, stderr = self.connection.send_command(hsrp_config_commands)

            if stderr:
                logging.error(f"Error during HSRP configuration: {stderr}")
            else:
                logging.info(f"HSRP configuration completed successfully on {self.name} ({self.ip})")
                print(f"HSRP configuration output:\n{stdout}")

        except Exception as e:
            logging.error(f"An error occurred while configuring HSRP on {self.name} ({self.ip}): {e}")
            raise
        finally:
            # Ensure the connection is closed even if an error occurs
            logging.info(f"Closing connection to device {self.name} ({self.ip})")
            self.connection.close()