# 🧠 XFS Inode Scanner

A forensic utility to scan and analyze **XFS filesystem images** for inode metadata, including support for:

- Allocated inode inspection  
- Deleted inode heuristics  
- Short-form directory entries detection

---

## 📦 Features

- ✅ Detects valid XFS filesystem via magic number check (`XFSB`)
- 📁 Scans all inodes (512-byte aligned) for:
  - File type
  - Access/modification/change times
- ⚰️ Identifies likely deleted inodes (based on type and timestamps)
- 📂 Detects short-form directory inodes (inlined entries)
- 🧾 Optional integration with `xfs_ncheck` for filename mapping

---

## 📖 Usage

```bash
./xfs_inode_scanner.py [-h] [-a | -d | -s] image_path
```
---

| Option              | Description                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------- |
| `-h`, `--help`      | Show help message and exit                                                                        |
| `-a`, `--allocated` | List only **allocated inodes** — i.e., inodes that have a known file type and valid timestamps    |
| `-d`, `--deleted`   | List only **probably deleted inodes** — identified by missing file type but with valid timestamps |
| `-s`, `--shortform` | Scan for **short-form directory entries** — small directory entries stored directly in the inode  |

