#!/usr/bin/env python3
"""
Calculadora de rede IPv4
Aceita:
  - 192.168.1.10/24
  - 192.168.1.10 255.255.255.0
  - 10.0.0.1/30
Saída: network, netmask, prefixo, broadcast, gateway sugerido, hosts válidos, etc.
"""
import ipaddress
import sys

def parse_input(argv):
    if len(argv) == 1:
        s = argv[0].strip()
        if '/' in s:
            return s  # pass through CIDR format
        else:
            raise ValueError("Formato inválido. Use IP/CIDR ou 'IP MASCARA'.")
    elif len(argv) == 2:
        ip = argv[0].strip()
        mask = argv[1].strip()
        # se máscara vier como prefixo (ex: /24), juntar
        if mask.startswith('/'):
            return f"{ip}{mask}"
        # se máscara vier como dotted-decimal, converter montando rede via host/net
        try:
            # ip_network aceita "ip/mask" diretamente only; montar string combinada:
            # Precisamos descobrir prefix len a partir da máscara dotted
            prefix = ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
            return f"{ip}/{prefix}"
        except Exception as e:
            raise ValueError(f"Máscara inválida: {mask}") from e
    else:
        raise ValueError("Use: script.py <IP/CIDR>  OU  script.py <IP> <MASCARA>")

def summarize(target):
    # target: string como "192.168.1.10/24"
    try:
        # Criar IPv4Interface para manter IP do host + rede
        iface = ipaddress.IPv4Interface(target)
    except Exception as e:
        raise ValueError(f"Entrada inválida: {target}") from e

    ip = iface.ip
    network = iface.network  # IPv4Network
    netmask = network.netmask
    prefix = network.prefixlen
    broadcast = network.broadcast_address

    # Número total de endereços na rede
    total_addrs = network.num_addresses

    # Hosts utilizáveis:
    if prefix >= 31:
        # /31 tem 2 endereços usados em ponto-a-ponto (sem hosts "normais")
        # /32 é apenas o próprio host
        usable_hosts = []
        first_usable = None
        last_usable = None
        num_usable = 0
        gateway = None
    else:
        # hosts() gera só os endereços "hosts" (exclui network e broadcast)
        hosts_list = list(network.hosts())
        num_usable = len(hosts_list)
        if num_usable > 0:
            first_usable = hosts_list[0]
            last_usable = hosts_list[-1]
            # Sugestão de gateway: primeiro host utilizável
            gateway = first_usable
        else:
            first_usable = last_usable = gateway = None

    # wildcard (inversa da máscara)
    wildcard_int = int(netmask._ip) ^ 0xFFFFFFFF
    wildcard = ipaddress.IPv4Address(wildcard_int)

    result = {
        "input_ip": str(ip),
        "network_address": str(network.network_address),
        "netmask": str(netmask),
        "prefix": f"/{prefix}",
        "broadcast": str(broadcast),
        "total_addresses": total_addrs,
        "num_usable": num_usable,
        "first_usable": str(first_usable) if first_usable else "N/A",
        "last_usable": str(last_usable) if last_usable else "N/A",
        "gateway_suggestion": str(gateway) if gateway else "N/A",
        "wildcard": str(wildcard),
    }
    return result

def pretty_print(d):
    print(f"Input IP:           {d['input_ip']}")
    print(f"Network:            {d['network_address']} {d['prefix']}")
    print(f"Netmask:            {d['netmask']}")
    print(f"Wildcard:           {d['wildcard']}")
    print(f"Broadcast:          {d['broadcast']}")
    print(f"Total endereços:    {d['total_addresses']}")
    print(f"Hosts utilizáveis:  {d['num_usable']}")
    print(f"Primeiro host:      {d['first_usable']}")
    print(f"Último host:        {d['last_usable']}")
    print(f"Gateway sugerido:   {d['gateway_suggestion']}")


if __name__ == "__main__":
    # Uso simples pela linha de comando
    # Exemplos:
    #   python3 ipcalc.py 192.168.1.10/24
    #   python3 ipcalc.py 10.0.0.2 255.255.255.252
    try:
        if len(sys.argv) <= 1:
            print("Uso: ipcalc.py <IP/CIDR>  OU  ipcalc.py <IP> <MASCARA>")
            print("Exemplos: ipcalc.py 192.168.1.10/24")
            print("          ipcalc.py 10.0.0.2 255.255.255.252")
            sys.exit(1)

        args = sys.argv[1:]
        target = parse_input(args)
        out = summarize(target)
        pretty_print(out)
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(2)
