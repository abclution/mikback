# mikback - Simple, multiple Mikrotik device backup system

Simple backup script for multiple Mikrotik devices written in Python\*

* Please make sure ssh and scp from your shell is availiable in your path.
* Tested and written on Debian 12


# USAGE

* Generate a new public/private keypair or re-use your existing to use on the next step.
* Create a "admin-backup" or similar user on each device.
* Upload your public key to the device using winbox, and assign it to your new user.
* Create or edit a `devices.json` file in the script's root folder.
* Run the script, `python mikback.py`
* Inspect your success.


## Create a user on each Mikrotik device.

Highly recommended to create a standalone user on each device with FULL access. This is the only way to ensure that the script can read/write to the device and create backups.
It also follows best security practices. You may create multiple public/private keypairs and define each one individually in the `devices.json` file.
This is useful for re-use of the same authentication for multiple backup locations without compromising a central master user.

* Create a new user on each device with FULL access.
  * Winbox on user creation requests a password and I suggest a long, random password that should be immediately forgotten as you should never use it.
* Generate a new public/private keypair on your local machine, or re-use your existing keypair.
* Upload your public key to the device using winbox, add the user and in system -> users -> SSH Keys -> Import SSH Key -> Type your new username and select the Key File from the device.

## devices.json

This is the file where you should define your devices. It is a json file and is mostly self explanatory.

```json
{
    "device1": {                           // This is the device definition, it can be any unique name.
        "DEVICE_NAME": "Mikrotik-A",       // Used in naming the export and backup files. NO SPACES OR WHITESPACE, also name should be unique otherwise your files will overwrite each other if you have the same name and base path between them.
        "DEVICE_IP": "192.168.22.1",       // IP of the device
        "DEVICE_PORT": 5522,               // SSH Port of the device
        "DEVICE_USERNAME": "admin-ssh",    // Username (you should create a new user with FULL access on the device)
        "DEVICE_PASSWORD": "ajsdfasdfasdf",// Password entered here will force password authentication. Leave null or "" to use keypair authenticaion.
        "DEVICE_ROS7": true,               // Enable/disable RouterOS 7.x export type (show-sensitive). RouterOS 6.x is the default.
        "SSH_OPTIONS": "-oPubkeyAcceptedAlgorithms=+ssh-rsa", // Needed for most Mikrotik devices
        "BASE_PATH": "./backups/",         // Local destination root for exports and backups.
        "EXPORT": true,                    // Enable/disable Mikrotik config exports. Must enable at least one of VERBOSE/COMPACT types as well.
        "EXPORT_TERSE": true,              // Enable Terse export for both VERBOSE and COMPACT. Terse is highly recommended.
        "EXPORT_VERBOSE": true,            // Verbose export, contains all config values.
        "EXPORT_COMPACT": true,            // Compact export, contains only values changed from default settings.
        "BACKUP": true,                    // Must be true to create and download a Mikrotik binary .backup file
        "BACKUP_PASSWORD": "sdfggdf"       // Password used to encrypt the binary backup, set to null (no quotations) or "" (double quotations) to disable encryption.

    }
}
```

`BASE_PATH`

The base path folder *MUST* exist otherwise the script will error. It will not make the directory/folder it for you and undefined behaviors will occur if it does not exist first.


`BACKUP`

If `BACKUP` is set to true, a backup will be created. Whether it is encrypted or not is up to how `BACKUP_PASSWORD` is set.


`BACKUP_PASSWORD`

To disable encryption of the binary backup, `BACKUP_PASSWORD` must be set to null, no quotations.

ex. `“BACKUP_PASSWORD”: null` or can be set to an empty string `“BACKUP_PASSWORD”: ""`

`DEVICE_NAME`

As long as all `DEVICE_NAME` are unique, the `BASE_PATH` can be the same for all devices.

`SSH_OPTIONS`

Mikrotik devices use older crypto libraries. The default value of `-o PubkeyAcceptedAlgoriths=ssh-rsa` should work for most Mikrotik devices. This enables a depreciated crypto which most modern Linux distros have disabled by default as it is consider insecure. \*\* Most Mikrotik devices require some form of this option for successful password-less login.\*\*

For even older versions of Mikrotik, you may need this instead: `"-o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa"`


# Mikrotik Export Options Explained


* /export - The export command prints a script that can be used to restore configuration.  The default export, what it exports exactly depends on the version of RouterOS. Starting from v6rc1, `/export` behavior is identical to `/export compact`. For prior RouterOS `/export` behavior is equivalent to `/export verbose`

Due to this behavior, the script requires defining the export type for each device in the `devices.json` file. You can choose multiple export types.

* /export terse - This is actually a switch that can be applied to any of the export types. Terse is highly recommended as it produces every configuration line on a separate line instead of splitting long lines up into multiple lines.
* /export compact - Starting from v5.12 compact export was added. It allows to export only part of configuration that is not default RouterOS config.
* /export verbose - Contains all values.



