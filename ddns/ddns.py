from asyncio import set_event_loop, SelectorEventLoop
from json import dumps
from selectors import SelectSelector
from aiohttp import ClientSession, InvalidURL
from .utils import Config

api_url = "https://api.cloudflare.com/client/v4/zones/"
HEADERS = None
baseheader = {"Authorization": 'Bearer ', "Content-Type": "application/json"}
ip_url = Config.ip_urls()
IPV6_fail = False


class Entry:
    def __init__(self, zoneid: str, subdomain: str, iptype: str, proxied: bool, ip: str, create: bool = False,
                 subdomain_id: str = None, ttl: int = 1):
        """
        Class for the single config entrys. 
        
        :param zoneid: Zone ID of the Domain
        :param subdomain: Full domain
        :param iptype: Type of the entry. Can be 'A' or 'AAAA'
        :param proxied: should the entry be proxied
        :param ip: IP of the entry
        :param create: Create entry if not exists
        :param subdomain_id: Cloudflare domain ID
        :param ttl: time to life for the entry
        """
        self.subdomain = subdomain
        self.type = iptype
        self.proxied = proxied
        self.creation = create
        self.zone = zoneid
        self.id = subdomain_id
        self.ttl = ttl
        self.ip = ip
        self.data = {"type": self.type, "name": self.subdomain, "content": self.ip, "ttl": self.ttl,
                     "proxied": self.proxied}

    def __str__(self) -> str:
        """
        Casts custom entry ID
        :return entry_id:
        """
        return f"{self.subdomain.split('.')[0]}:{self.type}"

    async def create(self):
        """
        Creates the entry
        """
        if self.creation:
            async with ClientSession() as session:
                response = await session.post(api_url + self.zone + "/dns_records/", data=dumps(self.data),
                                              headers=HEADERS)
                if response.status == 200:
                    print(f"Create Entry for {self.subdomain:40} with IP {self.ip:39} | Status : {response.status:3}")
                else:
                    print(self.subdomain, await response.text(), response.status)
                await session.close()
        else:
            print(f"Entry shouldn't be created {self.subdomain:40} | Config setup")

    async def update(self):
        """
        Updates the entry
        """
        async with ClientSession() as session:
            response = await session.put(api_url + self.zone + "/dns_records/" + self.id,
                                         data=dumps(self.data), headers=HEADERS)
            if response.status == 200:
                print(f"Updated Entry for {self.subdomain:40} with IP {self.ip:39} | Status : {response.status:3}")
            else:
                print(self.subdomain, await response.text(), response.status)
            await session.close()


async def ipv_basic_urls(session: ClientSession, ip: str) -> str:
    """
    Used when no urls given
    :param session: aiohttp client session
    :param ip: Type of the searched IP, could be 'IPv4' or 'IPv6'
    :return ipv: of basic domain
    """
    url = "https://1.1.1.1/cdn-cgi/trace" if ip == "IPv4" else "https://[2606:4700:4700::1111]/cdn-cgi/trace"
    ipv_response = await session.get(url)
    return [line.split('=') for line in str(await ipv_response.text()).split('\n') if "ip=" in line][0][1]


async def ipv_address(ip: str) -> str:
    """
    Returns your Ipv4 or IPv6
    :param ip: Type of the searched IP, could be 'IPv4' or 'IPv6'
    :return ipv: for the given IP type
    """
    global IPV6_fail
    async with ClientSession() as session:
        try:
            ipv_response = await session.get(ip_url[ip])
            if ipv_response.status not in [200, 401, 402]:
                ipv = await ipv_basic_urls(session, ip)
            else:
                ipv = await ipv_response.text()
        except InvalidURL:
            ipv = await ipv_basic_urls(session, ip)
        except OSError:
            if ip == "IPv6":
                IPV6_fail, ipv = True, None
                print("""IPv6 Address can't be recieved!\nAll IPv6 related Features are deactivated""")
        await session.close()
        return ipv


async def get_cloudflare_entries(token: str, zone_id: str) -> list:
    """
    Gets your entries from cloudflare
    :param token: Cloudflare token
    :param zone_id: Cloudflare zone ID
    :return entries: from cloudflare
    """
    async with ClientSession() as session:
        global HEADERS
        HEADERS = baseheader.copy()
        HEADERS['Authorization'] += token
        raw_response = await session.get(api_url + zone_id + "/dns_records", headers=HEADERS)
        response = await raw_response.json()
        await session.close()
        return list(filter(lambda entry: entry['type'] in ['A', 'AAAA'], response['result']))


async def run():
    """
    Main runner for the Programm. Don't touch!
    """
    cfg_domains = Config.domains()
    ipv4 = await ipv_address("IPv4")
    ipv6 = await ipv_address("IPv6")

    for domain in cfg_domains.keys():
        raw_conf_entries = list(filter(lambda entry: entry['type'] in ['A', 'AAAA'], cfg_domains[domain]["Entries"]))
        raw_cldf_entries = await get_cloudflare_entries(cfg_domains[domain]["API"]['Token'],
                                                        cfg_domains[domain]["API"]['ZoneID'])

        cldf_different_ip = list(filter(lambda cldf: cldf['content'] not in [ipv6, ipv4], raw_cldf_entries))
        cldf_same_ip = [x for x in raw_cldf_entries if x not in cldf_different_ip]

        conf_ids = {f"{entry['name']}:{entry['type']}" for entry in raw_conf_entries}
        cldf_diffrent_ip_ids = {
            f"{entry['name'].split('.')[0]}:{entry['type']}"
            for entry in cldf_different_ip
        }

        cldf_same_ip_ids = {
            f"{entry['name'].split('.')[0]}:{entry['type']}"
            for entry in cldf_same_ip
        }

        new_entries_ids = conf_ids.difference(cldf_diffrent_ip_ids).difference(cldf_same_ip_ids)
        update_entries_ids = conf_ids.intersection(cldf_diffrent_ip_ids)

        for entry_dict in raw_conf_entries:
            entry_cfg: Entry = Entry(cfg_domains[domain]["API"]['ZoneID'],
                                     entry_dict['name'] + "." + domain,
                                     entry_dict['type'],
                                     entry_dict['proxied'],
                                     ipv4 if entry_dict['type'] == 'A' else ipv6,
                                     entry_dict['create'], ttl=entry_dict.get("ttl", 1))
            if str(entry_cfg) in new_entries_ids:
                await entry_cfg.create()
            elif str(entry_cfg) in update_entries_ids:
                cldf_entry = list(
                    filter(lambda cldf, cfge=entry_cfg: cfge.subdomain == cldf['name'] and cfge.type == cldf['type'],
                           cldf_different_ip))
                entry_cfg.id = cldf_entry[0]['id']
                await entry_cfg.update()
        for entry in cldf_same_ip:
            print(f"Nothing changed in {entry['name']:40} | {entry['type']:4}: {entry['content']}")


def main():
    """
    Starts main runner asynchronous
    """
    selector = SelectSelector()
    loop = SelectorEventLoop(selector)
    set_event_loop(loop)
    loop.run_until_complete(run())
    loop.close()
