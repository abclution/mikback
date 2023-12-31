#!/usr/bin/env python3

import os
import datetime
import subprocess
import json

# Uncomment this area if you want UTC time. Default is local time stamps.
# Get the current UTC date and time
# current_datetime = datetime.datetime.utcnow()

# Get the local date and time
current_datetime = datetime.datetime.now()

# Format the date and time
DATESTAMP = current_datetime.strftime("%Y-%m-%d-%s")


# Load device settings from the devices configuration file
with open("devices.json") as config_file:
    devices = json.load(config_file)


def get_mikrotik_export(device_name, file_name, export_type=""):
    '''SSH into the device and grabs the output of the Mikrotik export function
    and writes to local file'''
    device_settings = devices.get(device_name)

    if not device_settings:
        print(f"Device '{device_name}' not found in the configuration file.")
        return

    if device_settings["DEVICE_ROS7"] is True:
        if device_settings["DEVICE_PASSWORD"] is None or device_settings["DEVICE_PASSWORD"] == "":
            sh_command = f'ssh -i {device_settings["DEVICE_SSHKEY"]} {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/export {export_type} show-sensitive"'
        else: # Make command for password based login.
            sh_command = f'sshpass -e ssh {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/export {export_type} show-sensitive"'

    else:
        if device_settings["DEVICE_PASSWORD"] is None or device_settings["DEVICE_PASSWORD"] == "":
            sh_command = f'ssh -i {device_settings["DEVICE_SSHKEY"]} {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/export {export_type}"'
        else:  # Make command for password based login.
            sh_command = f'sshpass -e ssh {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/export {export_type}"'


    # Run the SSH command and capture the output to a file
    with open(f'{device_settings["BASE_PATH"]}/{file_name}', "w") as output_file:
        try:
            # Set the environment variable
            os.environ["SSHPASS"] = f'{device_settings["DEVICE_PASSWORD"]}'
            subprocess.run(sh_command, shell=True, stdout=output_file, check=True)
            print(f"Export saved to {device_settings['BASE_PATH']}/{file_name}")

            if "SSHPASS" in os.environ:
                os.environ.pop("SSHPASS")

        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e}")


def get_mikrotik_backup(device_name, file_name, backup_password=None):
    """Creates a backup of the device's configuration and saves it to a file on
    the device. Then uses SCP to copy the file to the local machine. Finally
    uses SSH again and removes the file from the device."""

    device_settings = devices.get(device_name)

    if not device_settings:
        print(f"Device '{device_name}' not found in the configuration file.")
        return

    if backup_password is None or backup_password == "":
        if device_settings["DEVICE_PASSWORD"] is None or device_settings["DEVICE_PASSWORD"] == "":
            sh_command = f'ssh -i {device_settings["DEVICE_SSHKEY"]} {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/system backup save dont-encrypt=yes name={file_name}"'

        else:  # Make command for password based login.
            sh_command = f'sshpass -e ssh {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/system backup save dont-encrypt=yes name={file_name}"'

    else:
        if device_settings["DEVICE_PASSWORD"] is None or device_settings["DEVICE_PASSWORD"] == "":
            sh_command = f'ssh -i {device_settings["DEVICE_SSHKEY"]} {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/system backup save encryption=aes-sha256 password={backup_password} name={file_name}"'
        else:  # Make command for password based login.
            sh_command = f'sshpass -e ssh {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/system backup save encryption=aes-sha256 password={backup_password} name={file_name}"'


    if device_settings["DEVICE_PASSWORD"] is None or device_settings["DEVICE_PASSWORD"] == "":
        # Retrieve binary backup command
        scp_command = f'scp -i {device_settings["DEVICE_SSHKEY"]} {device_settings["SSH_OPTIONS"]} -P {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]}:/{file_name} {device_settings["BASE_PATH"]}'

        # Cleanup the backup file command
        clean_command = f'ssh -i {device_settings["DEVICE_SSHKEY"]} {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/file remove {file_name}"'

    else:  # Make command for password based login.
        scp_command = f'sshpass -e scp {device_settings["SSH_OPTIONS"]} -P {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]}:/{file_name} {device_settings["BASE_PATH"]}'
        clean_command = f'sshpass -e ssh {device_settings["SSH_OPTIONS"]} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/file remove {file_name}"'

    try:

        # Set the environment variable
        os.environ["SSHPASS"] = f'{device_settings["DEVICE_PASSWORD"]}'

        subprocess.run(sh_command, shell=True, stdout=subprocess.DEVNULL, check=True)
        print(f"Created {file_name} on {device_name}\n")

        subprocess.run(scp_command, shell=True, stdout=None, check=True)
        print(f"Backup retrieved from {device_name}, and saved to: {device_settings['BASE_PATH']}/{file_name} \n")

        subprocess.run(clean_command, shell=True, stdout=None, check=True)
        print(f"{file_name} removed from {device_name}.")

        if "SSHPASS" in os.environ:
            os.environ.pop("SSHPASS")

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")


for device in devices:
    if devices[device]["BACKUP"] is True:
        get_mikrotik_backup(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}.backup", devices[device]["BACKUP_PASSWORD"], )

    if devices[device]["EXPORT"] is True:

        if devices[device]["EXPORT_TERSE"] is True:

            if devices[device]["EXPORT_COMPACT"] is True:
                get_mikrotik_export(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}-COMPACT_TERSE.rsc","compact terse",)

            if devices[device]["EXPORT_VERBOSE"] is True:
                get_mikrotik_export(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}-VERBOSE_TERSE.rsc","verbose terse",)
        else:

            if devices[device]["EXPORT_COMPACT"] is True:
                get_mikrotik_export(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}-COMPACT.rsc","compact",)

            if devices[device]["EXPORT_VERBOSE"] is True:
                get_mikrotik_export(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}-VERBOSE.rsc","verbose",)
