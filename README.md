# XFS-Inode-Parser


└──╼ $./xfs_inode_scanner.py -h
usage: xfs_inode_scanner.py [-h] [-a] [-d] [-s] image_path

Scan XFS filesystem image for inode metadata.

positional arguments:
  image_path       Path to XFS image file or device

options:
  -h, --help       show this help message and exit
  -a, --allocated  List only allocated inodes (inodes with type and all timestamps)
  -d, --deleted    List only 'Probably Deleted File' inodes
  -s, --shortform  Scan for short-form directory Entries
