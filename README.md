# Cloudflare DynDNS Script
Python script to dynamically update multiple cloudflare records on one zonefile with your actual IP.

    Set up the config and run the script. 
    It then will automatically update your records all X seconds

# Config Values
## API:

Key | Value | Description
-------- | -------- | ---------
Token: | "EeGbyD6UTlCjECrXDUZ3td7lnQKBm3W2b4leZ2CyPW" | Cloudflare API Token for your Domain
ZoneID: | "oTsvYKAs3NudvxFztjgEuNRpuLzthJbs" | Zone ID for your Domain
config_timer: | 120 | Loop Timer
    
## Domains:

Key | Value | Description
-------- | -------- | ---------
"name": | "www.example.com" | Full Domain Name including subdomain
"type": | "A" | Record type (can be A or AAAA)
"proxied": | True | should the domain be proxies over cloudflare
"create": | True | should the domain be created if not existing
   
# Usage:

## Installation
    python -m pip3 install aiohttp

## Start:
    python3 ddns.py