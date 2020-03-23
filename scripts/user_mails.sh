#/bin/bash

## Check arguments
if [ $# -eq 0 ]; then
    echo "No arguments supplied"; exit 1
fi

if ! id -u "$1" ; then
    echo "User does not exists"; exit 1
fi
USER=$1

## Create the backup config directory if it does not exist
bk_path="/volume1/homes/$USER/Backup-Config"
mkdir -p "$bk_path"
config_path="$bk_path/SYN-02_$(date +%Y%m%d%M%S).dss"
config_name="${config_path::-4}.tar.xz"

## Export the backup config and check whether it was sucessful
synoconfbkp export --filepath="$config_path"
if [[ ! ( -f $config_path && -r $config_path ) ]]; then
    echo 1>&2 "Synology .dss config dump not readable"
    exit 2
fi

## Interprete the dss file as tar-archive and extract it
cp "$config_path" "$config_name"
tar --warning=no-timestamp -Jxf "$config_name" -C "$bk_path"

## Open the database and extrace the users and mail addresses
sqlite3 -column "$bk_path"/ConfigBkp/_Syno_ConfBkp.db <<!
.mode csv
.separator , "\n"
.output "/volume1/homes/$USER/users.csv"
SELECT name, description, mail FROM confbkp_user_tb WHERE mail != "";
!

## Remove unnecessary description suffix
chown -R "$USER:users" "/volume1/homes/$USER/users.csv"

## Cleanup
sudo rm -rf "$bk_path"
