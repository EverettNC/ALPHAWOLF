"""
AlphaVox - Voice Diagnostics Tool
-------------------------------
This tool provides detailed diagnostics for the voice system, helping with troubleshooting
and verification of voice differentiation.
"""

import hashlib
import json
import os
from datetime import datetime

from gtts import gTTS


def get_file_md5(filename):
    """Calculate MD5 hash of a file."""
    with open(filename, "rb") as f:
        md5 = hashlib.md5()
        while chunk := f.read(8192):
            md5.update(chunk)
    return md5.hexdigest()


def test_voice_with_details(text="This is a test of the voice system", lang="en"):
    """Test different TLDs and languages with detailed output."""

    # Define test configurations
    tlds = [
        {"code": "com", "name": "US English"},
        {"code": "co.uk", "name": "UK English"},
        {"code": "com.au", "name": "Australian English"},
        {"code": "ca", "name": "Canadian English"},
        {"code": "co.in", "name": "Indian English"},
        {"code": "co.za", "name": "South African English"},
        {"code": "ie", "name": "Irish English"},
    ]

    # Speed configurations
    speed_options = [{"name": "Slow", "slow": True}, {"name": "Normal", "slow": False}]

    results = []

    # Generate directory name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_dir = f"voice_test_{timestamp}"
    os.makedirs(test_dir, exist_ok=True)

    # Create report file
    report_path = os.path.join(test_dir, "voice_report.txt")

    with open(report_path, "w") as report:
        report.write("AlphaVox Voice System Diagnostic Report\n")
        report.write("======================================\n\n")
        report.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"Test Text: '{text}'\n")
        report.write(f"Language: {lang}\n\n")

        # Test each combination
        for tld in tlds:
            for speed in speed_options:
                # Create descriptive filename
                tld_code = tld["code"].replace(".", "_")
                speed_name = speed["name"].lower()
                filename = f"{tld_code}_{speed_name}.mp3"
                filepath = os.path.join(test_dir, filename)

                # Generate voice
                tts = gTTS(text=text, lang=lang, slow=speed["slow"], tld=tld["code"])

                # Save to file
                tts.save(filepath)

                # Get file details
                file_size = os.path.getsize(filepath)
                file_hash = get_file_md5(filepath)

                # Record result
                result = {
                    "tld": tld["code"],
                    "region": tld["name"],
                    "speed": speed["name"],
                    "filename": filename,
                    "file_size": file_size,
                    "md5": file_hash,
                }
                results.append(result)

                # Write to report
                report.write(
                    f"Configuration: {tld['name']} ({tld['code']}), Speed: {speed['name']}\n"
                )
                report.write(f"  Filename: {filename}\n")
                report.write(f"  File Size: {file_size} bytes\n")
                report.write(f"  MD5 Hash: {file_hash}\n\n")

        # Analyze uniqueness
        unique_hashes = set(r["md5"] for r in results)
        report.write(f"Uniqueness Analysis\n")
        report.write(f"------------------\n")
        report.write(f"Total Configurations: {len(results)}\n")
        report.write(f"Unique Outputs: {len(unique_hashes)}\n\n")

        # Group identical outputs
        if len(unique_hashes) < len(results):
            report.write("Identical Output Groups:\n")
            hash_groups = {}

            for result in results:
                hash_val = result["md5"]
                if hash_val not in hash_groups:
                    hash_groups[hash_val] = []
                hash_groups[hash_val].append(
                    f"{result['region']} ({result['tld']}), Speed: {result['speed']}"
                )

            for i, (hash_val, configs) in enumerate(hash_groups.items(), 1):
                if len(configs) > 1:
                    report.write(f"Group {i}:\n")
                    for config in configs:
                        report.write(f"  - {config}\n")
                    report.write("\n")

    print(f"Voice diagnostic complete. Report saved to {report_path}")
    return results


if __name__ == "__main__":
    test_voice_with_details()
