# mykrotik-backup

Simple backup script for multiple mikrotik devices written in Python\*

\*It actually needs ssh and scp from your shell, tested and written on Debian 12




:::info
The script has a global ssh option of “PubkeyAcceptedAlgoriths=ssh-rsa” which most modern distros have disabled by default as it is consider insecure. Mikrotik devices require this for passwordless login.

:::

## devices.json

This is the file where you should define your devices. It is a json file and is mostly self explanatory. 

```json
{
    "device1": {                       // This is the device definition, it can be any unique name.
        "DEVICE_NAME": "Mikrotik-A",   // The device name itself, used in nameing the export and backup files. Also should be unique otherwise your files will overwrite each other.
        "DEVICE_IP": "192.168.22.1",   // IP of the device
        "DEVICE_PORT": 5522,           // SSH Port of the device
        "DEVICE_USERNAME": "admin-ssh",// Username (you should create a new user with FULL access on the device)
        "DEVICE_SSHKEY": "~/.ssh/id_rsa",// The private key used for login, the default will be your user default
        "BASE_PATH": "./configs/",       // Local destination root for exports and backups.
        "EXPORT": false,               // Mikrotik supports multiple forms when exporting. This is the "basic" export
        "EXPORT_VERBOSE": false,       // Verbose export
        "EXPORT_TERSE": false,         // Terse export
        "EXPORT_COMPACT": false,       // Compact export
        "BACKUP": true,                // Must be true to create and download a Mikrotik binary .backup file
        "BACKUP_PASSWORD": "sdfggdf"   // Password used to encrypt the binary backup, set to null (no quotations) to disable encryption.

    }
}
```


