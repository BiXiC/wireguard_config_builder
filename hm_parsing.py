import socket
import time
import random
import json
import os
import copy


def creat_base_json(path):
    sites = ['hm.com', 'cos.com', 'cosstores.com', 'arket.com']
    ips = {}
    for site in sites:
        ips[site] = []
    with open(path, 'w') as outfile:
        json.dump(ips, outfile)


def get_ipv4_by_hostname(hostname):
    addr_info = socket.getaddrinfo(hostname, 8080)
    ip = [i[4][0] for i in addr_info if i[0] is socket.AddressFamily.AF_INET]
    return list(dict.fromkeys(ip))


def dict_len(dict):
    length = 0
    for k, v in dict.items():
        length += len(v)
    return length


def main():
    path = "external_sites.json"
    if not os.path.isfile(path):
        creat_base_json(path)

    with open(path) as file:
        ips_old = json.load(file)

    counter = 0
    ips_new = copy.deepcopy(ips_old)
    ips_old_length = dict_len(ips_old)
    while True:
        delta_time = random.uniform(1, 10)
        counter += delta_time
        time.sleep(delta_time)
        for site in ips_new.keys():
            site_ip_list = get_ipv4_by_hostname(site)
            ips_new[site] = list(set(ips_new[site]).union(set(site_ip_list)))

        if counter > 60 * 10:
            ips_new_length = dict_len(ips_new)
            if ips_new_length != ips_old_length:
                with open(path, 'w') as outfile:
                    json.dump(ips_new, outfile)
            ips_old = copy.deepcopy(ips_new)
            ips_old_length = dict_len(ips_old)
            counter = 0


if __name__ == '__main__':
    main()