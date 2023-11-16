#!/usr/bin/env python3

import sys
import argparse
import ipaddress
import maxminddb
import tabulate
from tabulate import SEPARATING_LINE

def process_input(input_stream):
    asn_db_path = './databases/GeoLite2-ASN.mmdb'
    country_db_path = './databases/GeoLite2-Country.mmdb'
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

            yield format_simple(row, asn, city_reader.get(row), prefix_len)


def is_valid(value):
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False

    # check if it is local or meta ip
    return not ip.is_private and not ip.is_reserved and not ip.is_multicast and not ip.is_unspecified


def format_simple(ip, asn_data, city_data, prefix_len):
    # Extract the desired data if available, or use 'N/A' if not provided
    asn = asn_data.get('autonomous_system_number', 'N/A') if asn_data else 'N/A'
    org = asn_data.get('autonomous_system_organization', 'N/A') if asn_data else 'N/A'

    # Extract city and country names
    city = city_data.get('city', {}).get('names', {}).get('en', 'N/A') if city_data and 'city' in city_data else 'N/A'
    country = city_data.get('country', {}).get('names', {}).get('en',
                                                                'N/A') if city_data and 'country' in city_data else 'N/A'

    ip_network = ipaddress.ip_network(f"{ip}/{prefix_len}", strict=False)
    network_start_ip = ip_network.network_address

    # Create location line
    location_line = f"{city}, {country}"

    # Create range notation based on prefix length
    range_notation = f"/{prefix_len}" if prefix_len is not None else ""

    return asn, org, ip, f"{network_start_ip}{range_notation}", location_line


# Function to sort by ASN and IP sequence number
def sort_key(row):
    asn, ip, subnet = [row[0], row[2], row[3]]

    ip = ipaddress.ip_address(ip)
    network = ipaddress.ip_network(subnet, strict=False)

    return int(asn), int(network.network_address), int(ip)


def main():
    parser = argparse.ArgumentParser(description='Process each row of a file or stdin data.')
    parser.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='The input file to process. If omitted, stdin is used.')

    args = parser.parse_args()

    result = []
    with args.input_file as input_stream:
        for r in process_input(input_stream):
            result.append(r)

    result = sorted(result, key=sort_key)

    for i in range(1, len(result)):
        prev_asn = result[i - 1][0]
        curr_asn = result[i][0]

        if prev_asn != curr_asn and prev_asn != SEPARATING_LINE:
            result.insert(i, SEPARATING_LINE)

    print(
        tabulate.tabulate(result, headers=["ASN", "ORG", "IP", "Network", "Location"], tablefmt="rst")
    )


if __name__ == "__main__":
    main()
