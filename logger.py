#!/usr/bin/env python3
"""
logger.py

Serial-to-CSV logger for the Mesh Gateway.

Usage:
    python logger.py --port /dev/ttyUSB0 --baud 115200 --out gateway_log.csv

The script parses lines like:
  [SENT] to 3 seq 1 len 11
  [FWD] from 101 -> 3 seq 1 newttl 4
  [DELIVER] from 1 seq 37 ttl 2 len 5: Hello
  [ERROR] Duplicate ignored from src=2 seq=5

It writes CSV rows:
timestamp, direction, src, dst, seq, ttl, len, payload_text, raw_line
"""

import argparse
import csv
import serial
import time
import re
from datetime import datetime

LINE_PATTERNS = {
    'SENT': re.compile(r'^\[SENT\]\s+to\s+(\d+)\s+seq\s+(\d+)\s+len\s+(\d+)', re.IGNORECASE),
    'FWD' : re.compile(r'^\[FWD\]\s+from\s+(\d+)\s+->\s+(\d+)\s+seq\s+(\d+)\s+newttl\s+(\d+)', re.IGNORECASE),
    'DELIVER': re.compile(r'^\[DELIVER\]\s+from\s+(\d+)\s+seq\s+(\d+)\s+ttl\s+(\d+)\s+len\s+(\d+):\s*(.*)', re.IGNORECASE),
    'ERROR': re.compile(r'^\[ERROR\]\s+(.*)', re.IGNORECASE)
}

def parse_line(line):
    line = line.strip()
    for kind, pat in LINE_PATTERNS.items():
        m = pat.match(line)
        if not m:
            continue
        if kind == 'SENT':
            dst = int(m.group(1))
            seq = int(m.group(2))
            length = int(m.group(3))
            return {
                'direction': 'SENT', 'src': None, 'dst': dst, 'seq': seq,
                'ttl': None, 'len': length, 'payload_text': ''
            }
        if kind == 'FWD':
            src = int(m.group(1)); dst = int(m.group(2))
            seq = int(m.group(3)); ttl = int(m.group(4))
            return {
                'direction': 'FWD', 'src': src, 'dst': dst, 'seq': seq,
                'ttl': ttl, 'len': None, 'payload_text': ''
            }
        if kind == 'DELIVER':
            src = int(m.group(1)); seq = int(m.group(2))
            ttl = int(m.group(3)); length = int(m.group(4)); payload = m.group(5).strip()
            return {
                'direction': 'DELIVER', 'src': src, 'dst': None, 'seq': seq,
                'ttl': ttl, 'len': length, 'payload_text': payload
            }
        if kind == 'ERROR':
            msg = m.group(1).strip()
            return {
                'direction': 'ERROR', 'src': None, 'dst': None, 'seq': None,
                'ttl': None, 'len': None, 'payload_text': msg
            }
    # fallback: unknown
    return None

def main():
    p = argparse.ArgumentParser(description='Mesh Gateway Serial Logger -> CSV')
    p.add_argument('--port', '-p', required=True, help='Serial port (e.g. /dev/ttyUSB0 or COM3)')
    p.add_argument('--baud', '-b', type=int, default=115200)
    p.add_argument('--out', '-o', default='gateway_log.csv')
    p.add_argument('--append', action='store_true', help='Append to existing CSV instead of creating new')
    args = p.parse_args()

    csv_exists = args.append
    csvfile = open(args.out, 'a' if args.append else 'w', newline='', encoding='utf-8')
    writer = csv.writer(csvfile)
    if not args.append:
        writer.writerow(['timestamp', 'direction', 'src', 'dst', 'seq', 'ttl', 'len', 'payload_text', 'raw_line'])

    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
        print(f'Connected to {args.port} @ {args.baud}')
    except Exception as e:
        print('ERROR opening serial port:', e)
        return

    try:
        while True:
            raw = ser.readline().decode('utf-8', errors='ignore').strip()
            if not raw:
                time.sleep(0.05)
                continue
            ts = datetime.utcnow().isoformat() + 'Z'
            parsed = parse_line(raw)
            if parsed is None:
                # write as unknown error row
                writer.writerow([ts, 'UNKNOWN', None, None, None, None, None, '', raw])
                csvfile.flush()
                print('[UNKNOWN]', raw)
                continue
            row = [
                ts,
                parsed['direction'],
                parsed['src'],
                parsed['dst'],
                parsed['seq'],
                parsed['ttl'],
                parsed['len'],
                parsed['payload_text'],
                raw
            ]
            writer.writerow(row)
            csvfile.flush()
            print(ts, parsed['direction'], parsed['src'], parsed['dst'], parsed['seq'], parsed['ttl'], parsed['len'], parsed['payload_text'])
    except KeyboardInterrupt:
        print('Exiting (keyboard interrupt)')
    except Exception as e:
        print('Error during serial read:', e)
    finally:
        csvfile.close()
        ser.close()

if __name__ == '__main__':
    main()