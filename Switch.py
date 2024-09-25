"""
Module responsible for switch configurations.
"""
from Device import Device
import logging

class Switch(Device):
    """
    Class responsible for switch-specific configurations, including security, STP, and VLAN settings.
    """

    def config_Security(self) -> None:
        """
        Configures port security on a specified switch interface.
        :return: None
        """
        try:
            logging.info(f"Starting security configuration on {self.name} ({self.ip})")
            self.connection.connect(self.priv_exec_pass)

            # User inputs
            interface = input("Enter the name of the interface for security configuration (e.g., 'GigabitEthernet0/1'): ").strip()
            vlan = input("Enter the VLAN ID to allow on the interface: ").strip()

            # Constructing and sending the command
            command = (
                f"interface {interface}\n"
                f"switchport mode access\n"
                f"switchport access vlan {vlan}\n"
                f"switchport port-security\n"
            )
            stdout, stderr = self.connection.send_command(command)

            if stderr:
                logging.error(f"Error in security configuration: {stderr}")
            else:
                print(f"Security configuration successful on interface {interface}:\n{stdout}")

        except Exception as e:
            logging.error(f"An error occurred during security configuration: {e}")
            raise
        finally:
            self.connection.close()

    def config_STP(self) -> None:
        """
        Configures Spanning Tree Protocol (STP) settings on the switch, including setting primary and secondary VLANs.
        :return: None
        """
        try:
            logging.info(f"Starting STP configuration on {self.name} ({self.ip})")
            self.connection.connect(self.priv_exec_pass)

            # Prompting user for VLAN inputs
            primary_vlan = input("Enter the VLAN ID to set as primary (or 'q' to skip): ").strip()
            secondary_vlan = input("Enter the VLAN ID to set as secondary (or 'q' to skip): ").strip()

            # Building the STP configuration command
            stp_command = "spanning-tree mode rapid-pvst\n"
            if primary_vlan != 'q':
                stp_command += f"spanning-tree vlan {primary_vlan} root primary\n"
            if secondary_vlan != 'q':
                stp_command += f"spanning-tree vlan {secondary_vlan} root secondary\n"

            if 'q' in [primary_vlan, secondary_vlan]:
                logging.warning("Skipping some VLAN root settings based on user input.")

            # Sending the command
            stdout, stderr = self.connection.send_command(stp_command)

            if stderr:
                logging.error(f"Error in STP configuration: {stderr}")
            else:
                print(f"STP configuration successful:\n{stdout}")

        except Exception as e:
            logging.error(f"An error occurred during STP configuration: {e}")
            raise
        finally:
            self.connection.close()

    def config_Vlan(self) -> None:
        """
        Configures a VLAN on the switch by creating a new VLAN with a specified ID and name.
        :return: None
        """
        try:
            logging.info(f"Starting VLAN configuration on {self.name} ({self.ip})")
            self.connection.connect(self.priv_exec_pass)

            # Prompting user for VLAN ID and name
            vlan_id = input("Enter the VLAN ID to create (e.g., '10'): ").strip()
            vlan_name = input("Enter the name of the VLAN (e.g., 'Management_VLAN'): ").strip()

            if not vlan_id.isdigit():
                raise ValueError(f"VLAN ID should be numeric. Received: {vlan_id}")

            # Constructing and sending the VLAN configuration command
            vlan_command = f"vlan {vlan_id}\nname {vlan_name}\n"
            stdout, stderr = self.connection.send_command(vlan_command)

            if stderr:
                logging.error(f"Error in VLAN configuration: {stderr}")
            else:
                print(f"VLAN {vlan_id} ({vlan_name}) created successfully:\n{stdout}")

        except ValueError as ve:
            logging.error(f"Invalid input: {ve}")
            print(f"Error: {ve}")
        except Exception as e:
            logging.error(f"An error occurred during VLAN configuration: {e}")
            raise
        finally:
            self.connection.close()
