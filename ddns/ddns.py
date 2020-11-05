import asyncio
import copy
import json

import aiohttp

from .utils import Config

api_url = "https://api.cloudflare.com/client/v4/zones/"
HEADERS = None
baseheader = {"Authorization": f'Bearer ', "Content-Type": "application/json"}
ip_url = Config.ip_urls()
IPV6_fail = False


async def ipv4_address():
    async with aiohttp.ClientSession() as session:
        ipurl = ip_url["IPv4"]
        ipv4_raw_response = await session.get(ipurl)
        await session.close()
        return await ipv4_raw_response.text()


async def ipv6_address():
    global IPV6_fail
    async with aiohttp.ClientSession() as session:
        try:
            ipv6_raw_response = await session.get(ip_url["IPv6"])
            await session.close()
            return await ipv6_raw_response.text()
        except OSError:
            IPV6_fail = True
            print("""IPv6 Address can't be recieved!\nAll IPv6 related Features are deactivated""")


async def get_cloudflare_entries(token, zone_id):
    async with aiohttp.ClientSession() as session:
        global HEADERS
        HEADERS = copy.deepcopy(baseheader)
        HEADERS['Authorization'] += token
        raw_response = await session.get(api_url + zone_id + "/dns_records", headers=HEADERS)
        response = await raw_response.json()
        await session.close()
        return response['result']


async def compare_new_entries(config_entries, cloudflare_entries):
    new_entries = []
    cfdl_names = [cfdl_entry['name'] for cfdl_entry in cloudflare_entries]
    for cfg_entry in config_entries:
        if cfg_entry['name'] not in cfdl_names and cfg_entry not in new_entries and cfg_entry['create']:
            new_entries.append(cfg_entry)
    return new_entries


async def compare_update_entries(cfg_entries, cloudflare_entries):
    given_entries = []
    cfdl_names = [cfdl_entry['name'] for cfdl_entry in cloudflare_entries]
    for cfg_entry in cfg_entries:
        if cfg_entry['name'] in cfdl_names and cfg_entry not in given_entries:
            given_entries.append(cfg_entry)
    return given_entries


async def filter_new_list(record_type, new_entries_list):
    filtered = []
    for cfg_entry in new_entries_list:
        if cfg_entry['type'] == record_type and cfg_entry not in filtered:
            filtered.append(cfg_entry)
    return filtered


async def process_new_entries(ip, entry, zoneid):
    data = json.dumps(
        {"type": entry['type'], "name": entry['name'], "content": ip,
         "ttl": 1, "proxied": entry['proxied']})
    await create_entry(entry, data, ip, zoneid)


async def process_update_entries(ip, entry, cloudflare_entry, zoneid):
    for cdfl_entry in cloudflare_entry:
        if entry['name'] == cdfl_entry['name'] and entry['type'] == cdfl_entry['type'] \
                and str(ip) != cdfl_entry['content']:
            data = json.dumps(
                {"type": entry['type'], "name": entry['name'], "content": ip,
                 "ttl": 1, "proxied": entry['proxied']})
            await update_entry(entry, cdfl_entry['id'], data, ip, zoneid)
            return
    print(f"No update needed for Entry: {entry['name']}")


async def run():
    cfg_domains = Config.domains()
    for domain in cfg_domains.keys():
        cldf_entries = await get_cloudflare_entries(cfg_domains[domain]["API"]['Token'],
                                                    cfg_domains[domain]["API"]['ZoneID'])
        cldf_ipv4_entries = await filter_new_list("A", cldf_entries)
        cldf_ipv6_entries = await filter_new_list("AAAA", cldf_entries)

        ipv4_entries = await filter_new_list("A", cfg_domains[domain]["Entries"])
        ipv6_entries = await filter_new_list("AAAA", cfg_domains[domain]["Entries"])

        new_ipv4_entries = await compare_new_entries(ipv4_entries, cldf_ipv4_entries)
        ipv4 = await ipv4_address()
        for cfg_entry in new_ipv4_entries:
            await process_new_entries(ipv4, cfg_entry, zoneid=cfg_domains[domain]["API"]['ZoneID'])
            new_ipv4_entries.remove(cfg_entry)

        ipv4_update_entries = await compare_update_entries(ipv4_entries, cldf_ipv4_entries)
        for cfg_entry in ipv4_update_entries:
            await process_update_entries(ipv4, cfg_entry, cldf_ipv4_entries,
                                         zoneid=cfg_domains[domain]["API"]['ZoneID'])
        if not IPV6_fail:
            ipv6 = await ipv6_address()
            new_ipv6_entries = await compare_new_entries(ipv6_entries, cldf_ipv6_entries)
            for cfg_entry in new_ipv6_entries:
                await process_new_entries(ipv6, cfg_entry, zoneid=cfg_domains[domain]["API"]['ZoneID'])
                new_ipv6_entries.remove(cfg_entry)

            ipv6_update_entries = await compare_update_entries(ipv6_entries, cldf_ipv6_entries)
            for cfg_entry in ipv6_update_entries:
                await process_update_entries(ipv6, cfg_entry, cldf_ipv6_entries,
                                             zoneid=cfg_domains[domain]["API"]['ZoneID'])


async def update_entry(config_entry, cloudflare_entry_id, datas, ip, zoneid):
    async with aiohttp.ClientSession() as session:
        put = await session.put(api_url + zoneid + "/dns_records/" + cloudflare_entry_id,
                                data=datas, headers=HEADERS)
        if int(put.status) == 200:
            print(f"Updated Entry for {config_entry['name']} with IP {ip}. Status : {put.status}")
        await session.close()


async def create_entry(config_entry, datas, ip, zoneid):
    async with aiohttp.ClientSession() as session:
        post = await session.post(api_url + zoneid + "/dns_records/", data=datas, headers=HEADERS)
        if int(post.status) == 200:
            print(f"Create Entry for {config_entry['name']} with IP {ip}. Status : {post.status}")
        await session.close()


async def amain():
    task = asyncio.create_task(run())
    await task


def main():
    asyncio.run(amain())
