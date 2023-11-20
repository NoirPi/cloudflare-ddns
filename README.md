# Cloudflare DynDNS Script
Simple Pythonscript to dynamically update multiple cloudflare records on one zonefile with your actual IP.

    Set up the config and run the script. 
    It then will automatically update your records all X seconds

# Config Values

The config is stored in `/etc/ddns/` and will be generated on the first run.

## IP URLS

IPv4 = URL to get the plain text IPv4 address
IPv6 = URL to get the plain text IPv6 address


## API:

| Key           | Value                                        | Description                          |
|---------------|----------------------------------------------|--------------------------------------|
| Token:        | "EeGbyD6UTlCjECrXDUZ3td7lnQKBm3W2b4leZ2CyPW" | Cloudflare API Token for your Domain |
| ZoneID:       | "oTsvYKAs3NudvxFztjgEuNRpuLzthJbs"           | Zone ID for your Domain              |
## Domains:

| Key        | Value             | Description                                  |
|------------|-------------------|----------------------------------------------|
| "name":    | "www.example.com" | Full Domain Name including subdomain         |
| "type":    | "A"               | Record type (can be A or AAAA)               |
| "proxied": | True              | should the domain be proxies over cloudflare |
| "create":  | True              | should the domain be created if not existing |

# Usage:

## Installation

```bash
pip install -U https://github.com/NoirPi/cloudflare-ddns/archive/multiple.zip # For latest version
pip install -U https://github.com/NoirPi/cloudflare-ddns/archive/<commithash>.zip # For a specific version
```

Then simply use with:

```bash
ddns
or 
/usr/bin/env ddns
```

or add the following crontab to run the script every 5 minutes: 

```diff
- # This specific crontab requires syslog on your system:
*/5 * * * * ddns 2>&1 | logger -t dyndns
```
You can check the crontab with ``grep 'dyndns' /var/log/syslog``


## Systemd Service
You can also use the example systemd service files in the systemd folder which reruns the service every 10 minutes:
```diff
wget https://github.com/NoirPi/cloudflare-ddns/blob/multiple/systemd/ddns.service -O /etc/systemd/system/ddns.service
wget https://github.com/NoirPi/cloudflare-ddns/blob/multiple/systemd/ddns.timer -O /etc/systemd/system/ddns.timer
systemctl enable ddns.service && systemctl enable ddns.timer 
systemctl daemon-reload && systemctl restart ddns.timer
```


## Uninstalling

To uninstall simply use

```bash
pip uninstall cloudflare-ddns
```

## Contributing

To contribute, fork and clone the repo, and install dependencies with 

```bash
python setup.py develop
```