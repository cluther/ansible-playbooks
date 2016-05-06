import re

from Products.ZenRRD.CommandParser import CommandParser
from Products.ZenUtils.Utils import prepId


class iptables(CommandParser):

    def processResults(self, cmd, result):
        components = {}

        for line in cmd.result.output.splitlines():
            match = re.match(
                r'^Chain (?P<chain>\S+) \(policy \S+ '
                r'(?P<packets>\d+) packets, '
                r'(?P<bytes>\d+) bytes\)$',
                line)

            if match:
                component_id = prepId(match.group("chain"))
                if component_id not in components:
                    components[component_id] = {}

                for measure in ("packets", "bytes"):
                    value = int(match.group(measure))
                    components[component_id][measure] = value

        for point in cmd.points:
            if point.component in components:
                values = components[point.component]
                if point.id in values:
                    result.values.append((point, values[point.id]))
