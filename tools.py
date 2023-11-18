import argparse
from dataclasses import dataclass, field
import json
import os
import sys
from typing import Iterator, Optional
from subprocess import Popen, PIPE


class GoTool:
    _name = None

    @classmethod
    def is_installed(cls):
        return cls.get_bin_path() is not False

    @classmethod
    def get_bin_path(cls):
        go_path = os.environ.get('GOPATH')
        bin_path = os.path.join(go_path, 'bin', cls._name)

        if go_path is None or not os.path.exists(bin_path):
            return False

        return bin_path


@dataclass
class DnsxRecord:
    host: str
    status_code: str
    timestamp: str
    resolver: list[str]
    a: list[str] = field(default_factory=list)
    cname: list[str] = field(default_factory=list)
    soa: list[str] = field(default_factory=list)


class DnsxTool(GoTool):
    _name = 'dnsx'

    @classmethod
    def process(cls, input_stream) -> Iterator[DnsxRecord]:
        if not cls.is_installed():
            print(f'Command {tool._name} not found', file=sys.stderr)
            sys.exit(1)

        cmd_bin = cls.get_bin_path()

        # Run the command
        process = Popen([cmd_bin, '-a', '-json', '-cname'], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(input_stream)
        output = [out_row for out_row in stdout.decode('utf-8').split('\n') if len(out_row) > 0]

        for json_row in output:
            row = json.loads(json_row)
            yield DnsxRecord(**row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process each row of a file or stdin data.')
    parser.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin,
                        help='The input file to process. If omitted, stdin is used.')

    args = parser.parse_args()

    tool = DnsxTool()

    for r in tool.process(args.input_file):
        print(r)
