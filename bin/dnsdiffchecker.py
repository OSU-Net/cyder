from sys import argv
import re


if len(argv) != 3:
    print "USAGE: dnsdiffchecker.py <DIFF FILE> <MIGRATION LOGS>"
    exit()

diff_file = argv[1]
log_file = argv[2]


def arpify(ip):
    ip = '.'.join(reversed(ip.split('.')))
    ip += ".in-addr.arpa"
    return ip

diffmatches, logmatches = {}, {}
logmatches["delegated"] = re.compile(".*migrate host (.*) because it is in a delegated")
logmatches["staticrange"] = re.compile(".*Static interface (.*) has been disabled.*IP must be in a static range")
logmatches["ctnr"] = re.compile(".*Could not .* (\S*): {.*ctnr does not match its domain")
logmatches["noreverse"] = re.compile(".*Could not migrate .*: {.*No reverse domain found for (\S*)']}")
logmatches["noreversestatic"] = re.compile(".*Could not create the static interface \S*: {.*No reverse domain found for (\S*)']}")
logmatches["ignoreptr"] = re.compile(".*Ignoring PTR (\S*); .*exists")
logmatches["ignorea"] = re.compile(".*Ignoring AR (\S*); .*exists")
logmatches["cnamectnr"] = re.compile("CNAME (\S*) has mismatching container")
logmatches["secondary"] = re.compile(".*Domain (\S*) is a secondary, so")

diffmatches["delegated"] = lambda label, line: label in line and "in ptr" not in line
diffmatches["delegated.ptr"] = lambda label, line: label in line and "in ptr" in line
diffmatches["staticrange"] = lambda hostname, line: hostname in line
diffmatches["ctnr"] = lambda name, line: name in line
diffmatches["noreverse"] = lambda ip, line: arpify(ip) in line
diffmatches["noreversestatic"] = lambda ip, line: ip in line and "in a" in line
diffmatches["noreverse.a"] = lambda ip, line: ip in line and "in a" in line
diffmatches["ignoreptr"] = lambda ip, line: arpify(ip) in line and "in ptr" in line
diffmatches["ignorea"] = lambda ip, line: ip in line and "in a" in line
diffmatches["cnamectnr"] = lambda name, line: line.startswith(name) and "in cname" in line
diffmatches["secondary"] = lambda name, line: line.split(' in ')[0].endswith(name + '.')
difflines = [line.strip('<').strip() for line in open(diff_file).readlines() if line and line[0] in '<>']

descriptions = {
    "delegated": "Ignored because their domain is in a delegated zone",
    "ctnr": "Ignored because Ctnr does not match the domain",
    "cnamectnr": "Ignored because Ctnr does not match the domain (CNAME)",
    "ignoreptr": "Ignored because static interface or PTR using this IP already exists",
    "noreversestatic": "Ignored because no appropriate reverse zone exists",
    }


removelines = {}
removelineset = set([])
dubiouslines = set([])
for key in diffmatches:
    removelines[key] = set([])

for line in open(log_file):
    line = line.strip()
    for key in logmatches:
        match = logmatches[key].match(line)
        if match:
            value = match.group(1)
            value = value.lower()
            for line2 in difflines:
                if line2[0] == ">":
                    continue
                line2 = line2.lower()
                match2 = diffmatches[key](value, line2)
                if match2:
                    removelines[key].add(line2)
                    removelineset.add(line2)
                    if key == "delegated":
                        for line3 in difflines:
                            match3 = diffmatches["delegated.ptr"](value, line3)
                            if match3:
                                removelines[key].add(line3)
                                removelineset.add(line3)
                    elif key == "noreverse":
                        for line3 in difflines:
                            match3 = diffmatches["noreverse.a"](value, line3)
                            if match3:
                                removelines[key].add(line3)
                                removelineset.add(line3)


for line in open(log_file):
    line = line.strip()
    for key in logmatches:
        match = logmatches[key].match(line)
        if match:
            value = match.group(1)
            value = value.lower()
            for line2 in difflines:
                if line2[0] == ">":
                    continue
                for key2 in diffmatches:
                    if '.' not in key2:
                        continue
                    basekey = key2.split('.')[0]
                    if key != basekey:
                        continue
                    match3 = diffmatches[key2](value, line2)
                    if match3:
                        if line2 in removelines[basekey]:
                            continue
                        removelines[key2].add(line2)
                        dubiouslines.add(line2)

for key in diffmatches:
    if not removelines[key]:
        continue

    if key in descriptions:
        print descriptions[key]
    else:
        print key

    if key == "secondary":
        print "%s records removed due to being in a secondary zone" % len(removelines[key])
        print
        continue

    for line in sorted(removelines[key]):
        print line
    print

print "DUBIOUS"
for line in dubiouslines:
    print line
print

print "UNKNOWN"
for line in sorted(difflines):
    if "soa" in line:
        continue
    if line not in removelineset and line not in dubiouslines:
        print line
