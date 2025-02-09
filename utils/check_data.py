import json
import datetime

# data = datetime.datetime.now(datetime.UTC).isoformat()[:-6]
# print(data)
# print(type(data))

jsondata = json.load(open("../data/example_hacker_data.json"))
badges = set()


for hacker in jsondata:
    badge_code = hacker["badge_code"]
    name = hacker.get("name")
    email = hacker.get("email")
    phone = hacker.get("phone")
    scans = hacker.get("scans")

    if badge_code in badges:
        print(f"Duplicate badge code: {badge_code}")
        print(hacker)
    badges.add(badge_code)

    if not name:
        print(f"Null name for badge code: {badge_code}")
    if not email:
        print(f"Null email for badge code: {badge_code}")
    if not phone:
        print(f"Null phone for badge code: {badge_code}")
    if not scans:
        print(f"Null scans for badge code: {badge_code}")
    else:
        for scan in scans:
            if not scan.get("activity_name"):
                print(f"Null activity_name in scan for badge code: {badge_code}")
            if not scan.get("activity_category"):
                print(f"Null activity_category in scan for badge code: {badge_code}")
            if not scan.get("scanned_at"):
                print(f"Null scanned_at in scan for badge code: {badge_code}")

