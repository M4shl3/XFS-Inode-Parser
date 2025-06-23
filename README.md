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



> 🟡 **This tool is currently in _beta_**.  
> Functionality is still being tested and refined. Expect updates, improvements, and possibly breaking changes in future versions.  




---






## 📖 Usage

```bash
./xfs_inode_scanner.py [-h] [-a | -d | -s] image_path
```
---

| Option              | Description                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------- |
| `-h` | Show help message and exit                                                                        |
| `-a` | List only **allocated inodes**     |
| `-d` | List only **probably deleted inodes**  |
| `-s` | Scan for **short-form directory entries**  |

