import os
import datetime
import subprocess
import json
# Get the current UTC date and time
#current_datetime = datetime.datetime.utcnow()

# Get the local date and time
current_datetime = datetime.datetime.now()

# Format the date and time
DATESTAMP = current_datetime.strftime("%Y-%m-%d-%s")

SSH_OPTIONS = "PubkeyAcceptedAlgorithms=ssh-rsa"

# Load device settings from the devices configuration file
with open('devices.json') as config_file:
    devices = json.load(config_file)

# Grabs the output of the Mikrotik export function and writes to local file
def get_mikrotik_export(device_name, file_name, export_type=""):

    device_settings = devices.get(device_name)

    if not device_settings:
        print(f"Device '{device_name}' not found in the configuration file.")
        return

    sh_command = f'ssh -o {SSH_OPTIONS} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/export {export_type}"'

    # Run the SSH command and capture the output to a file
    with open(f'{device_settings["BASE_PATH"]}/{file_name}', 'w') as output_file:
        try:
            subprocess.run(sh_command, shell=True, stdout=output_file, check=True)
            print(f"Command executed and output saved to {file_name}")
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e}")

# Creates a backup of the device's configuration and saves it to a file on the
# device. Then uses SCP to copy the file to the local machine. And finally
# uses SSH again and removes the file from the device.
def get_mikrotik_backup(device_name, file_name, backup_password=None):
    device_settings = devices.get(device_name)

    if not device_settings:
        print(f"Device '{device_name}' not found in the configuration file.")
        return

    if backup_password is None:
        sh_command = f'ssh -i {device_settings["DEVICE_SSHKEY"]} -o {SSH_OPTIONS} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/system backup save dont-encrypt=yes name={file_name}"'
    else:
        sh_command = f'ssh -i {device_settings["DEVICE_SSHKEY"]} -o {SSH_OPTIONS} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/system backup save encryption=aes-sha256 password={backup_password} name={file_name}"'

    # Retrieve binary backup
    scp_command = f'scp -i {device_settings["DEVICE_SSHKEY"]} -o {SSH_OPTIONS} -P {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]}:/{file_name} {device_settings["BASE_PATH"]}'

    # Cleanup the backup file
    clean_command = f'ssh -i {device_settings["DEVICE_SSHKEY"]} -o {SSH_OPTIONS} -p {device_settings["DEVICE_PORT"]} {device_settings["DEVICE_USERNAME"]}@{device_settings["DEVICE_IP"]} "/file remove {file_name}"'

    try:
        subprocess.run(sh_command, shell=True, stdout=subprocess.DEVNULL, check=True)
        print(f"Created {file_name} on device {device_name}\n")

        subprocess.run(scp_command, shell=True, stdout=None, check=True)
        print(f"Backup retrieved from device {device_name}.\n")

        subprocess.run(clean_command, shell=True, stdout=None, check=True)
        print(f"{file_name} removed from device {device_name}.")

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")



for device in devices:
    
    if devices[device]['BACKUP'] == True:
        get_mikrotik_backup(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}.backup", devices[device]['BACKUP_PASSWORD'])

    if devices[device]['EXPORT'] == True:
        get_mikrotik_export(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}.rsc")
    
    if devices[device]['EXPORT_COMPACT'] == True:
        get_mikrotik_export(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}-COMPACT.rsc", "compact")
    
    if devices[device]['EXPORT_VERBOSE'] == True:
        get_mikrotik_export(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}-VERBOSE.rsc", "verbose")
    
    if devices[device]['EXPORT_TERSE'] == True:
        get_mikrotik_export(device, f"{devices[device]['DEVICE_NAME']}_{DATESTAMP}-TERSE.rsc", "terse")






    # print(f"Device: {device['DEVICE_NAME']}")
    #print(device["DEVICE_NAME"])
    #print(type(device))
    #print("fart")
    #print(f"Device: {device[2]}")
    #print(devices[device]["DEVICE_NAME"])
    
# # Create and retrieve unencrypted binary backup.
# get_mikrotik_backup(f'{DEVICE_NAME}-{DATESTAMP}.backup')

# # Create and retrieve encrypted binary backup.
# get_mikrotik_backup(f'{DEVICE_NAME}-{DATESTAMP}.ENCRYPTED.backup', BACKUP_PASSWORD)

# # Create and capture standard export script.
# get_mikrotik_export(f'{DEVICE_NAME}-{DATESTAMP}_export.rsc')

# # Create and capture compact export script.
# get_mikrotik_export(f'{DEVICE_NAME}-{DATESTAMP}_export-compact.rsc', "compact")

# # Create and capture verbose export script.
# get_mikrotik_export(f'{DEVICE_NAME}-{DATESTAMP}_export-verbose.rsc', "verbose")

# # Create and capture terse export script.
# get_mikrotik_export(f'{DEVICE_NAME}-{DATESTAMP}_export-terse.rsc', "terse")