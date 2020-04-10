#  VS-Notification

VS-Notification is an extension for VS-Transmission and provides a notification service for users about new media available on the Synology's Video Station.

It's based on an automated toolchain which download, convert, rename and relocate video files for Synology's Video Station. Since this is an automatic process, users can be periodically notified when there are new video files.

Check out the the basic toolchain, starting with VS-Transmission (https://github.com/heimdall-syno/VS-Transmission).

## Quick Start

1. Clone the repository inside an arbitrary directory on the filesystem

2. Create a scheduled Task (settings - task planer) with the following settings:
	```
    Type:       User-defined script
    Task:       VS-Notification
    Schedule:   e.g. every Sunday - 12:00
    User:       root
    Command:    python3 /path/to/directory/VS-Notification/notification.py --name "ServiceName"
                                                                           --address "admin@service.com"
                                                                           --service "ServiceName"
                                                                           --subject "ServiceName - Releases"
                                                                           --receivers "users"
                                                                           --interval 7
                                                                           --date
    ```
----
#### Script configuration (arguments)

```
+-------------+------------------+------------------------------------------------+---------------------------+
|  Arguments  |    Description   |                    Function                    |          Examples         |
+-------------+------------------+------------------------------------------------+---------------------------+
| --name      |   Sender's name  |     Name which is shown in the mail header     |           "Name"          |
+-------------+------------------+------------------------------------------------+---------------------------+
| --address   | Sender's address |     Address which is used to send the mail     |    "admin@service.com"    |
+-------------+------------------+------------------------------------------------+---------------------------+
| --service   |   Service Name   |  Name of the service providing the meda files  |       "ServiceName"       |
+-------------+------------------+------------------------------------------------+---------------------------+
| --subject   |   Mail subject   |               Subject of the mail              |  "ServiceName - Releases" |
+-------------+------------------+------------------------------------------------+---------------------------+
| --receivers |  Mail receivers  |       Members who should receive the mail      |                           |
|             |                  |                                                | "users" -> All users      |
|             |                  |                                                +---------------------------+
|             |                  |                                                | "admin" -> All admins     |
|             |                  |                                                +---------------------------+
|             |                  |                                                | "all"   -> Users & admins |
+-------------+------------------+------------------------------------------------+---------------------------+
| --interval  |   Time interval  |       Days between two consecutive mails       |             7             |
+-------------+------------------+------------------------------------------------+---------------------------+
| --date      |  Date extension  | Whether to add the current date to the subject |            ---            |
+-------------+------------------+------------------------------------------------+---------------------------+
```
