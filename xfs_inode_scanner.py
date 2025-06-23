#!/usr/bin/python3
import sys
import os
import struct
import subprocess
from datetime import datetime
import argparse

# Constants
XFS_SUPERBLOCK_OFFSET = 0x0
XFS_SUPERBLOCK_MAGIC = b'XFSB'
INODE_MAGIC = b'IN'
INODE_SIZE = 512

FILE_TYPES = {
    0x1: 'FIFO',
    0x2: 'Character Device',
    0x4: 'Directory',
    0x6: 'Block Device',
    0x8: 'Regular File',
    0xA: 'Symlink',
    0xC: 'Socket',
}

def detect_xfs_magic(f):
    f.seek(XFS_SUPERBLOCK_OFFSET)
    return f.read(4) == XFS_SUPERBLOCK_MAGIC

def parse_file_type(mode_byte):
    return (mode_byte >> 4) & 0xF

def parse_times(block):
    try:
        atime = struct.unpack(">I", block[32:36])[0]
        mtime = struct.unpack(">I", block[40:44])[0]
        ctime = struct.unpack(">I", block[48:52])[0]
        return atime, mtime, ctime
    except:
        return 0, 0, 0

def format_time(epoch):
    try:
        return datetime.utcfromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Invalid"

def scan_and_classify_inodes(f, filesize):
    offset = 0
    inodes = []

    while offset < filesize:
        f.seek(offset)
        block = f.read(INODE_SIZE)
        if len(block) < 4:
            break

        if block[:2] == INODE_MAGIC:
            mode_byte = block[2]
            type_code = parse_file_type(mode_byte)
            atime, mtime, ctime = parse_times(block)
            inode_number = offset // INODE_SIZE

            inode = {
                'inode': inode_number,
                'type_code': type_code,
                'atime': atime,
                'mtime': mtime,
                'ctime': ctime
            }

            inodes.append(inode)

        offset += INODE_SIZE

    return inodes

def parse_xfs_ncheck(image_path):
    name_map = {}
    try:
        output = subprocess.check_output(['xfs_ncheck', image_path], stderr=subprocess.DEVNULL).decode()
        for line in output.strip().split('\n'):
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                inode = int(parts[0])
                name = parts[1].strip()
                name_map[inode] = name
    except Exception as e:
        print(f"Warning: Could not run xfs_ncheck - {e}")
    return name_map

def classify_and_print(inodes, name_map, only_allocated=False, only_deleted=False):
    total = 0
    for i, inode in enumerate(inodes):
        inode_num = inode['inode']
        type_code = inode['type_code']
        atime, mtime, ctime = inode['atime'], inode['mtime'], inode['ctime']
        has_times = all([atime, mtime, ctime])

        # Determine file type
        if inode_num == 128:
            file_type = "Root Directory"
        elif type_code == 0x0:
            prev_known = i > 0 and inodes[i - 1]['type_code'] in FILE_TYPES
            next_known = i + 1 < len(inodes) and inodes[i + 1]['type_code'] in FILE_TYPES
            if (prev_known or next_known) and has_times:
                file_type = "Probably Deleted File"
            else:
                file_type = "Unknown (0x0)"
        else:
            file_type = FILE_TYPES.get(type_code, f"Unknown (0x{type_code:X})")

        if only_allocated and (type_code == 0 or not has_times):
            continue

        if only_deleted and file_type != "Probably Deleted File":
            continue

        name = "." if inode_num == 128 else name_map.get(inode_num, "(unknown)")

        print(f"Inode #{inode_num:<7} | File Type: {file_type:<22} | Name: {name}")
        if has_times:
            print(f"  atime: {format_time(atime)}")
            print(f"  mtime: {format_time(mtime)}")
            print(f"  ctime: {format_time(ctime)}")
        total += 1

    print(f"\nTotal inodes found: {total}")

# Short-form inode scanning
def parse_shortform_inode(data, offset):
    inode = data[offset:offset+256]
    if len(inode) < 256 or inode[0:2] != b'IN':
        return None
    num_entries = inode[176]
    if num_entries == 0:
        return None
    inode_number = int.from_bytes(inode[152:160], byteorder='big')
    return {
        "inode_number": inode_number,
        "offset": offset,
        "entry_count": num_entries,
    }

def scan_shortform_inodes(data):
    offset = 0
    found = 0
    print("🔎 Scanning for short-form directory inodes...\n")
    while offset < len(data) - 256:
        if data[offset:offset+2] == b"IN":
            result = parse_shortform_inode(data, offset)
            if result:
                found += 1
                print(f"📁 Inode #{result['inode_number']}")
                print(f"  Physical Offset To The Inode: {result['offset']}")
                print(f"  Total short-form entries: {result['entry_count']}\n")
            offset += 256
        else:
            offset += 16
    if found == 0:
        print("❌ No short-form directory inodes found.")

def main(image_path, only_allocated=False, only_deleted=False, shortform=False):
    try:
        with open(image_path, 'rb') as f:
            print(f"Checking if '{image_path}' is an XFS filesystem...")
            if not detect_xfs_magic(f):
                print("❌ Not an XFS filesystem (magic 'XFSB' not found).")
                return
            print("✅ XFS filesystem detected.\n")

            if shortform:
                f.seek(0)
                data = f.read()
                scan_shortform_inodes(data)
                return

            f.seek(0, os.SEEK_END)
            filesize = f.tell()
            f.seek(0)

            inodes = scan_and_classify_inodes(f, filesize)
            if not inodes:
                print("No inodes found.")
                return

            name_map = parse_xfs_ncheck(image_path)
            classify_and_print(inodes, name_map, only_allocated, only_deleted)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan XFS filesystem image for inode metadata.")
    parser.add_argument("image_path", help="Path to XFS image file or device")
    parser.add_argument("-a", "--allocated", action="store_true", help="List only allocated inodes (inodes with type and all timestamps)")
    parser.add_argument("-d", "--deleted", action="store_true", help="List only 'Probably Deleted File' inodes")
    parser.add_argument("-s", "--shortform", action="store_true", help="Scan for short-form directory Entries")
    args = parser.parse_args()

    if sum([args.allocated, args.deleted, args.shortform]) > 1:
        print("❌ Error: Only one of -a, -d, or -s can be used at a time.")
        sys.exit(1)

    main(
        args.image_path,
        only_allocated=args.allocated,
        only_deleted=args.deleted,
        shortform=args.shortform
    )