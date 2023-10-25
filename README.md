# mykrotik-backup

Simple backup script for multiple mikrotik devices written in Python\*

* Please make sure ssh and scp from your shell is availiable in your path.
* Tested and written on Debian 12

This script has a global ssh option of `PubkeyAcceptedAlgoriths=ssh-rsa` which most modern Linux distros have disabled by default as it is consider insecure. ** Mikrotik devices require this for passwordless login.**

# USAGE

Create a admin-backup or similar user on each device.
Generate a new public/private keypair or re-use your existing.
Create or edit a `devices.json` file in the script's root folder.
Run the script., python mikback.py
Inspect your success.


## Create a user on each Mikrotik device.

Highly recommended to create a standalone user on each device with FULL access. This is the only way to ensure that the script can read/write to the device and create backups.
It also follows best security practices. You may create multiple public/private keypairs and define each one individually in the `devices.json` file. 
This is useful for re-use of the same authentication for multiple backup locations without compromising a central master user.

- Create a new user on each device with FULL access.
  - It requests a password and I suggest a long, random password that should be immediately forgotten as you should never use it.
- Generate a new public/private keypair or re-use your existing. 
- Upload your public key to the device using winbox, add the user and in system -> users -> SSH Keys -> Import SSH Key -> Type your new username and select the Key File from the device.

## devices.json

This is the file where you should define your devices. It is a json file and is mostly self explanatory.

```json
{
    "device1": {                          // This is the device definition, it can be any unique name.
        "DEVICE_NAME": "Mikrotik-A",      // The device name itself, used in nameing the export and backup files. Also should be unique otherwise your files will overwrite each other.
        "DEVICE_IP": "192.168.22.1",      // IP of the device
        "DEVICE_PORT": 5522,              // SSH Port of the device
        "DEVICE_USERNAME": "admin-ssh",   // Username (you should create a new user with FULL access on the device)
        "DEVICE_SSHKEY": "~/.ssh/id_rsa", // The private key used for login, the default will be your user default
        "BASE_PATH": "./configs/",        // Local destination root for exports and backups.
        "EXPORT": false,                  // Mikrotik supports multiple forms when exporting. This is the "basic" export. Any export enabled will export of that type. 
        "EXPORT_VERBOSE": false,          // Verbose export
        "EXPORT_TERSE": false,            // Terse export
        "EXPORT_COMPACT": false,          // Compact export
        "BACKUP": true,                   // Must be true to create and download a Mikrotik binary .backup file
        "BACKUP_PASSWORD": "sdfggdf"      // Password used to encrypt the binary backup, set to null (no quotations) to disable encryption.

    }
}
```

`BASE_PATH`
The base path folder *MUST* exist otherwise the script will error. It will not make the directory/folder it for you and undefined behaviors will occur if it does not exist first.


`BACKUP`
If BACKUP is set to true, a backup will be created. Whether it is encrypted or not is up to how `BACKUP_PASSWORD` is set.


`BACKUP_PASSWORD`
To disable encryption of the binary backup, `BACKUP_PASSWORD` must be set to null ex. `“BACKUP_PASSWORD”: null`


`DEVICE_NAME`
As long as all DEVICE_NAME are unique, the `BASE_PATH` can be the same for all devices.

