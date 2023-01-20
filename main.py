import sys
import csv
from apachelogs import LogParser
from datetime import timedelta

filter0 = {
        "max_requests": 40,
        "over": timedelta(seconds=60),
        "url": None,
        "ban_for": timedelta(seconds=600)
        }
filter1 = {
        "max_requests": 100,
        "over": timedelta(seconds=600),
        "url": None,
        "ban_for": timedelta(seconds=3600)
        }
filter2 = {
        "max_requests": 20,
        "over": timedelta(seconds=600),
        "url": "/login",
        "ban_for": timedelta(seconds=7200)
        }

filters = [filter0, filter1, filter2]


def is_ip_banned(ip, now):
    if ip in bans and now < bans[ip]:
        return True
    return False


def line_matches_filter(row, filter):
    row_url = row.request_line.split(" ")[1]
    if filter['url'] is not None and filter['url'] != row_url:
        return False
    return True


for filter in filters:
    filter['ip_buckets'] = {}

parser = LogParser(
    "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\""
    )
bans = {}
output = []

with open(sys.argv[1]) as log_file:
    for line in log_file:
        row = parser.parse(line)
        ip = row.remote_host
        now = row.request_time_fields['timestamp']
        banned_now = is_ip_banned(ip, now)

        for filter in filters:
            if line_matches_filter(row, filter):

                # Use existing bucket for previously parsed IP's
                if ip not in filter['ip_buckets']:
                    filter['ip_buckets'][ip] = []

                hits = 0
                for timestamp in filter['ip_buckets'][ip]:
                    if now - timestamp < filter['over']:
                        # count within tracked period against max
                        hits += 1
                    else:
                        # delete entries outside of tracked period
                        filter['ip_buckets'][ip].remove(timestamp)

                if not banned_now:
                    hits += 1
                    # Possibly ban
                    ban_until = None
                    if hits > filter['max_requests']:
                        ban_until = now + filter['ban_for']
                        # append to CSV list and ban dict
                        output.append([now.strftime('%s'), "BAN", ip])
                        output.append([ban_until.strftime('%s'), "UNBAN", ip])
                        bans[ip] = ban_until
                    # If not banned, add row to bucket
                    filter['ip_buckets'][ip].append(
                        row.request_time_fields['timestamp'])

# sort and write to csv
with open(sys.argv[1].split(".")[0] + ".csv", "a") as outputfile:
    outputwriter = csv.writer(outputfile)
    output = sorted(output)
    for o in output:
        outputwriter.writerow(o)