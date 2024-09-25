"""
Module responsible for managing SSH connectivity to network devices.
"""
import paramiko
import logging
from time import sleep


class DeviceConnection:
    """
    A class that handles SSH connection logic to network devices.
    Provides methods for establishing the connection, sending commands, and closing the session.
    """

    def __init__(self, ip, username, password):
        """
        Constructor for DeviceConnection.
        Initializes connection details like IP address, username, and password.

        :param ip: The IP address of the target device.
        :param username: The username for the SSH connection.
        :param password: The password for the SSH connection.
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.client = None
        self.shell = None

    def connect(self, priv_exec_pass, timeout=30) -> None:
        """
        Establishes an SSH connection to the device and enters privileged exec mode.

        :param priv_exec_pass: The password for privileged exec mode.
        :param timeout: Optional timeout for establishing the SSH connection.
        :raises: paramiko.SSHException if connection fails.
        """
        try:
            logging.info(f"Attempting to connect to {self.ip}...")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.ip, username=self.username, password=self.password, timeout=timeout)
            logging.info(f"SSH connection to {self.ip} established.")

            self.shell = self.client.invoke_shell()
            sleep(1)  # Allow time for shell to initialize
            self.shell.send(f'ena\n{priv_exec_pass}\nconf t\n')
            sleep(2)  # Allow time for the device to process privileged exec mode commands

            logging.info(f"Entered privileged exec mode on {self.ip}.")
        except paramiko.AuthenticationException:
            logging.error(f"Authentication failed while connecting to {self.ip}.")
            self.close()
        except paramiko.SSHException as e:
            logging.error(f"SSH error occurred while connecting to {self.ip}: {e}")
            self.close()
        except Exception as e:
            logging.error(f"An unexpected error occurred during connection to {self.ip}: {e}")
            self.close()

    def send_command(self, command):
        """
        Sends a command to the connected device and returns the output.

        :param command: The command to send.
        :return: A tuple of (output, error). Error will be None if successful, otherwise contains error message.
        """
        if not self.shell:
            error_msg = "No active SSH session. Please establish a connection first."
            logging.error(error_msg)
            return None, error_msg

        try:
            logging.info(f"Sending command to {self.ip}: {command}")
            self.shell.send(command + '\n')
            sleep(2)  # Allow time for the command to execute

            output = ""
            while self.shell.recv_ready():
                output += self.shell.recv(65535).decode('utf-8')

            logging.info(f"Command executed successfully on {self.ip}.")
            return output, None
        except paramiko.SSHException as e:
            logging.error(f"Failed to send command to {self.ip}: {e}")
            return None, str(e)
        except Exception as e:
            logging.error(f"An unexpected error occurred while sending command to {self.ip}: {e}")
            return None, str(e)

    def close(self) -> None:
        """
        Closes the SSH connection and cleans up resources.
        """
        if self.client:
            logging.info(f"Closing SSH connection to {self.ip}.")
            self.client.close()
            self.client = None
            self.shell = None
            logging.info(f"SSH connection to {self.ip} closed.")
        else:
            logging.info(f"No active connection to close for {self.ip}.")
