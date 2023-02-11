import argparse
import os
import stat
import socket
import json
from requests import get
import collections
from urllib.request import urlopen
from dataclasses import dataclass, field


@dataclass
class WgConf:
    user_name: str = 'default_peer_name'
    vpn_server_public_key: str = '...'
    vpn_server_endpoint: str = '...'
    vpn_user_privatekey: str = '...'
    vpn_user_ipv4: str = '...'
    additional_sites: list[str] = field(default_factory=list)
    ip_filter: bool = False
    config_save_folder: str = f'/home/{os.getenv("USER")}/Desktop'
    dns = '1.1.1.1'
    persistent_keep_alive = '30'
    allowed_ips = '0.0.0.0/0'

    @staticmethod
    def __get_community_antifilter_ip_list() -> list:
        ip_list_link = 'https://community.antifilter.download/list/community.lst'
        r = get(ip_list_link, allow_redirects=True)
        ip_list = r.content.decode("utf-8").split("\n")[:-1]
        return ip_list

    @staticmethod
    def _get_external_ip_list(json_file) -> list:
        with open(json_file) as file:
            ip = json.load(file)
        ip_list = list(ip.values())
        ip_list = sorted([ip for sublist in ip_list for ip in sublist])
        ip_list24 = ['.'.join(ip.split('.')[:-1])+'.0/24' for ip in ip_list]
        ip_list_counter = collections.Counter(ip_list24)
        ip_mask = list(ip_list_counter.keys())
        return ip_mask

    @staticmethod
    def _get_ipv4_by_hostname(hostname: str) -> list:
        addr_info = socket.getaddrinfo(hostname, 8080)
        ip = [i[4][0] for i in addr_info if i[0] is socket.AddressFamily.AF_INET]
        return list(dict.fromkeys(ip))

    def _get_additionl_ip_list(self) -> list:
        additional_ip = []
        for hostname in self.additional_sites:
            additional_ip.append(self._get_ipv4_by_hostname(hostname))
        additional_ip_flat = [item for sublist in additional_ip for item in sublist]
        return additional_ip_flat

    def _get_additional_ip_list_retry(self) -> list:
        external_ip = urlopen('https://ident.me').read().decode('utf8')
        assert external_ip == self.vpn_server_endpoint.split(':')[0], \
            "Turn on VPN before collecting domain's IP adresses"
        additional_ip = []
        for _ in range(10):
            additional_ip.append(self._get_additionl_ip_list())
        additional_ip_flat = [item for sublist in additional_ip for item in sublist]
        additional_ip_flat = [ip + '/32' for ip in set(additional_ip_flat)]
        return additional_ip_flat

    def get_full_ip_list(self):
        community_antifilter_ip = self.__get_community_antifilter_ip_list()
        additional_ip = self._get_additional_ip_list_retry()
        if 'external_sites.json' in os.listdir():
            external_ip = self._get_external_ip_list('external_sites.json')
            full_ip_list = set(community_antifilter_ip + additional_ip + external_ip)
        else:
            full_ip_list = set(community_antifilter_ip + additional_ip)
        return ', '.join(full_ip_list)

    def constuct_wg_conf(self) -> None:
        if self.ip_filter:
            self.allowed_ips = self.get_full_ip_list()
        structure = f"""
        [Interface]
        PrivateKey = {self.vpn_user_privatekey}
        Address = {self.vpn_user_ipv4}/32
        DNS = {self.dns}

        [Peer]
        PublicKey = {self.vpn_server_public_key}
        Endpoint = {self.vpn_server_endpoint}
        PersistentKeepalive = {self.persistent_keep_alive}
        AllowedIPs = {self.allowed_ips}
        """
        save_path = os.path.join(self.config_save_folder, f'{self.user_name}.conf')
        print(f'saving config file to {save_path}')
        with open(save_path, 'w') as f:
            f.write(structure)
        st = os.stat(save_path)
        os.chmod(save_path, st.st_mode | stat.S_IEXEC)


def main(additional_sites: list):
    parser = argparse.ArgumentParser(description='Construct Wireguard config file for peer')
    parser.add_argument('-u', '--user_name', required=False)
    parser.add_argument('-ip', '--vpn_user_ipv4', required=False)
    parser.add_argument('-pk', '--vpn_user_privatekey', required=False)
    parser.add_argument('-f', '--ip_filter', required=False)
    parser.add_argument('-s', '--save_folder', required=False)
    args = parser.parse_args()

    vpn_conf = WgConf(
        vpn_server_public_key=os.getenv('VPN_SERVER_PUBLIC_KEY'),
        vpn_server_endpoint=os.getenv('VPN_SERVER_ENDPOINT'),
        additional_sites=additional_sites,
        ip_filter=True)

    if args.user_name is not None:
        setattr(vpn_conf, 'user_name', args.user_name)
    if args.vpn_user_ipv4 is not None:
        setattr(vpn_conf, 'vpn_user_ipv4', args.vpn_user_ipv4)
    if args.vpn_user_privatekey is not None:
        setattr(vpn_conf, 'vpn_user_privatekey', args.vpn_user_privatekey)
    if args.ip_filter is not None:
        if args.ip_filter in ['1', 't', 'true', 'True']:
            setattr(vpn_conf, 'ip_filter', True)

    vpn_conf.constuct_wg_conf()


if __name__ == '__main__':
    additional_sites = ['rutracker.org', 'thepiratebay.org', 'hm.com', 'cos.com', 'cosstores.com', 'arket.com']
    main(additional_sites)