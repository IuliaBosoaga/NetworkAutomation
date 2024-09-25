"""
Module responsible for router configurations.
"""
from Device import Device
import logging

class Router(Device):

    def config_RipV2(self) -> None:
        """
        Method for configuring RIPv2 on a Router.
        Prompts the user for network details and whether static routes should be redistributed.
        :return: None
        """
        try:
            logging.info(f"Starting RIPv2 configuration on {self.name} ({self.ip})")
            self.connection.connect(self.priv_exec_pass)

            # Prompting user for network details
            network_1 = input("Enter the IP address of the first network: ").strip()
            network_2 = input("Enter the IP address of the second network: ").strip()
            redistrib = input("Do you want to redistribute the static routes from this device? (y/n): ").strip().lower()

            # Handling redistribution choice
            if redistrib == "y":
                redistribute_cmd = "redistribute static"
            elif redistrib == "n":
                redistribute_cmd = ""
            else:
                print("Invalid option. Static routes will not be redistributed.")
                redistribute_cmd = ""

            # Building the RIPv2 configuration command
            ripv2_command = (
                f"router rip\n"
                f"version 2\n"
                f"no auto-summary\n"
                f"network {network_1}\n"
                f"network {network_2}\n"
                f"{redistribute_cmd}\n"
            )

            # Sending the command to the router
            stdout, stderr = self.connection.send_command(ripv2_command)

            # Error handling for command execution
            if stderr:
                logging.error(f"Error during RIPv2 configuration: {stderr}")
            else:
                print(f"RIPv2 configuration successful:\n{stdout}")

        except Exception as e:
            logging.error(f"An error occurred during RIPv2 configuration: {e}")
            raise
        finally:
            self.connection.close()

    def setup_DHCP(self, ip: str) -> None:
        """
        Method for configuring DHCP services on a Router.
        :param ip: The router's IP address.
        :return: None
        """
        try:
            logging.info(f"Starting DHCP setup on {self.name} ({self.ip})")
            self.connection.connect(self.priv_exec_pass)

            # Deriving the base IP for the network
            ip_base = '.'.join(ip.split('.')[:3])

            # Prompting user for DHCP configuration details
            lan_id = input("Enter the ID of the LAN: ").strip()
            ip_pool = input("Enter the IP address of the DHCP pool: ").strip()
            subnet_mask = input("Enter the subnet mask: ").strip()

            try:
                switch_nr = int(input("Enter the number of switches in the LAN: ").strip())
                router_nr = int(input("Enter the number of routers in the LAN: ").strip())
            except ValueError:
                logging.error("Invalid input. Number of switches and routers must be integers.")
                print("Please enter valid numbers for the switches and routers.")
                return

            # Calculating the IP range for excluded addresses
            last_addr_b = router_nr + 1
            first_addr_e = 255 - switch_nr

            # Constructing the DHCP configuration command
            dhcp_command = (
                f"ip dhcp pool LAN{lan_id}\n"
                f"network {ip_pool} {subnet_mask}\n"
                f"default router {ip}\n"
                f"dns-server 8.8.8.8\n"
                f"exit\n"
                f"ip dhcp excluded-address {ip_base}.1 {ip_base}.{last_addr_b}\n"
                f"ip dhcp excluded-address {ip_base}.{first_addr_e} {ip_base}.254\n"
            )

            # Sending the DHCP configuration command
            stdout, stderr = self.connection.send_command(dhcp_command)

            # Error handling for command execution
            if stderr:
                logging.error(f"Error during DHCP setup: {stderr}")
            else:
                print(f"DHCP setup successful:\n{stdout}")

        except Exception as e:
            logging.error(f"An error occurred during DHCP setup: {e}")
            raise
        finally:
            self.connection.close()
