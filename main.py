#!/usr/bin/env python3
import os
import sys
import argparse
import ipaddress
import maxminddb
import tabulate
from tabulate import SEPARATING_LINE
from tools import DnsxTool, DnsxRecord
from typing import Iterator, Optional, Union

from dataclasses import dataclass, field


@dataclass
class Asn:
    autonomous_system_number: str
    autonomous_system_organization: str


@dataclass
class AsnLocation:
    country: dict[str, str] = field(default=None)
    city: dict[str, str] = field(default=None)
    continent: dict[str, str] = field(default=None)
    location: dict[str, str] = field(default=None)
    postal: dict[str, str] = field(default=None)
    registered_country: dict[str, str] = field(default=None)
    subdivisions: list[dict[str, str]] = field(default_factory=list)


@dataclass
class MaxMindRecord:
    ip: str
    location: AsnLocation = field(default=None)
    asn: Asn = field(default_factory=Asn)
    prefix_len: int = field(default=None)


def process_input(input_stream: list[str]) -> Iterator[MaxMindRecord]:
    asn_db_path = './databases/GeoLite2-ASN.mmdb'
    # country_db_path = './databases/GeoLite2-Country.mmdb'
    city_db_path = './databases/GeoLite2-City.mmdb'

    with (maxminddb.open_database(asn_db_path) as asn_reader,
          maxminddb.open_database(city_db_path) as city_reader):

        for row in input_stream:
            row = row.strip()

            if not is_valid(row):
                continue

            (asn, prefix_len) = asn_reader.get_with_prefix_len(row)

            if not asn:
                print('WARNING: ASN not found for IP: ' + row, file=sys.stderr)
            else:
                asn = Asn(**asn)

            location = city_reader.get(row)
            location = AsnLocation(**location) if location else None

            yield MaxMindRecord(ip=row, asn=asn, prefix_len=prefix_len, location=location)

            # yield format_simple(MaxMindRecord(ip=row, asn=asn, prefix_len=prefix_len, location=location))


def is_valid(value):
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False

    # check if it is local or meta ip
    return not ip.is_private and not ip.is_reserved and not ip.is_multicast and not ip.is_unspecified


def format_simple(record: MaxMindRecord):
    if record.asn:
        asn = record.asn.autonomous_system_number
        org = record.asn.autonomous_system_organization
    else:
        asn = 'N/A'
        org = 'N/A'

    if record.location:
        city = record.location.city.get('names', {}).get('en', 'N/A') if record.location.city else 'N/A'
        country = record.location.country.get('names', {}).get('en', 'N/A') if record.location.country else 'N/A'
        location_line = f"{city}, {country}"
    else:
        location_line = 'N/A'

    ip_network = ipaddress.ip_network(f"{record.ip}/{record.prefix_len}", strict=False)
    range_notation = f"{ip_network.network_address}/{record.prefix_len}" if record.prefix_len is not None else ""

    return asn, org, record.ip, range_notation, location_line


def format_dnsx_record(record: DnsxRecord):
    a_ips = '\n'.join(record.a if record.a else ['N/A'])
    cname_ips = '\n'.join(record.cname if record.cname else ['N/A'])


    return record.host, a_ips, cname_ips

# Function to sort by ASN and IP sequence number
def sort_key(is_dnsx=False):
    def sort(row: Union[MaxMindRecord, tuple[DnsxRecord, MaxMindRecord]]):
        if is_dnsx:
            _, maxmind_record = row
        else:
            maxmind_record: MaxMindRecord = row

        if not maxmind_record:
            raise ValueError('MaxMind record is None')

        asn = maxmind_record.asn.autonomous_system_number if maxmind_record.asn else 0
        ip = maxmind_record.ip
        subnet = maxmind_record.prefix_len

        try:
            ip = ipaddress.ip_address(ip)
            network = ipaddress.ip_network(subnet, strict=False)
        except ValueError:
            return to_int(asn), 0, 0

        return to_int(asn), int(network.network_address), int(ip)

    return sort


def to_int(value, default=0):
    try:
        return int(value)
    except ValueError:
        return default


def get_go_cmd_path(cmd_name):
    go_path = os.environ.get('GOPATH')

    if go_path is None:
        print('GOPATH is not set', file=sys.stderr)
        sys.exit(1)

    bin_path = os.path.join(go_path, 'bin', cmd_name)

    if not os.path.exists(bin_path):
        print(f'Command {cmd_name} not found', file=sys.stderr)
        sys.exit(1)

    return bin_path


def main():
    parser = argparse.ArgumentParser(description='Process each row of a file or stdin data.')
    parser.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='The input file to process. If omitted, stdin is used.')

    parser.add_argument('--dnsx', action='store_true', help='Use dnsx to resolve domains to IPs')

    args = parser.parse_args()

    result = []

    with args.input_file as input_stream:
        if args.dnsx:
            dnsx_tool = DnsxTool()
            dnsx_results: list[DnsxRecord] = list(dnsx_tool.process(input_stream))

            dnsx_ips = [ip for record in dnsx_results for ip in record.a]
            dnsx_result = process_input(dnsx_ips)
            lookup_results: dict[str, MaxMindRecord] = dict(zip(dnsx_ips, dnsx_result))

            for dnsx_record in dnsx_results:
                for ip in dnsx_record.a:
                    if lookup_result := lookup_results[ip]:
                        result.append((dnsx_record, lookup_result))
                    else:
                        print(f'WARNING: IP not found in MaxMind database: {ip}', file=sys.stderr)
                        result.append((dnsx_record, None))
        else:
            for r in process_input(input_stream):
                result.append(r)

    result = sorted(result, key=sort_key(args.dnsx))

    for i in range(1, len(result)):
        if result[i - 1] == SEPARATING_LINE:
            continue

        if args.dnsx:
            prev_dnsx_record, prev_maxmind_record = result[i - 1]
            dnsx_record, maxmind_record = result[i]
            prev_asn = prev_maxmind_record.asn.autonomous_system_number if prev_maxmind_record.asn else 0
            curr_asn = maxmind_record.asn.autonomous_system_number if maxmind_record.asn else 0
        else:
            prev_asn = result[i - 1].asn.autonomous_system_number if result[i - 1].asn else 0
            curr_asn = result[i].asn.autonomous_system_number if result[i].asn else 0

        if prev_asn != curr_asn:
            result.insert(i, SEPARATING_LINE)

    headers = ["ASN", "ORG", "IP", "Network", "Location"]
    table_rows = []

    if args.dnsx:
        headers = ["Host", "A", "CNAME"] + headers

        for rec in result:
            if rec == SEPARATING_LINE:
                table_rows.append(SEPARATING_LINE)
                continue

            dnsx_record, maxmind_record = rec
            table_rows.append(format_dnsx_record(dnsx_record) + format_simple(maxmind_record))
    else:
        for maxmind_record in result:
            table_rows.append(format_simple(maxmind_record))

    print(
        tabulate.tabulate(table_rows, headers=headers, tablefmt="mixed_grid")
    )


if __name__ == "__main__":
    main()
