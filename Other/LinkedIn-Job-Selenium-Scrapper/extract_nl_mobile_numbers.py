import re
import glob

# Pattern for Netherlands mobile numbers: +31 followed by 9 digits (can be improved for more formats)
mobile_pattern = re.compile(r"\+31[1-9][0-9]{8,9}")

# Collect all .log files in the current directory
log_files = glob.glob("*.log")

found_numbers = set()

for log_file in log_files:
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            matches = mobile_pattern.findall(line)
            for number in matches:
                found_numbers.add(number)

# Save results to a file
with open("netherlands_mobile_numbers.txt", "w") as out:
    for number in sorted(found_numbers):
        out.write(number + "\n")

print(f"Extracted {len(found_numbers)} Netherlands mobile numbers.")
