#!/usr/bin/env python3
"""
MobAI Pro Patcher v2.0
Usage: python patcher.py [patch|restore|check]

Applies 7 patches to MobAI_payload.exe (145MB Go 64-bit binary)
- patch:   apply all patches
- restore: restore from .bak backup
- check:   verify patch status

v2.0 fixes:
  - Fixed patches 6/7 that were at wrong addresses in v1.0
  - Added GetLimit -> -1 (fixes 100 limit)
  - Added "free" -> "pro" string overwrite + tier length fix
  - Added quota.NewManager limit init to -1
  - Dynamic PE parsing for robust RVA-to-file-offset mapping
"""

import sys, os, struct, shutil

TARGET = "MobAI_payload.exe"
BACKUP = "MobAI_payload.exe.bak"

# PE section parsing

def parse_pe_sections(filepath):
    sections = {}
    with open(filepath, "rb") as f:
        dos_header = f.read(64)
        pe_offset = struct.unpack_from("<I", dos_header, 0x3C)[0]
        f.seek(pe_offset)
        pe_sig = f.read(4)
        assert pe_sig == b"PE\0\0", "Not a valid PE file"
        coff = f.read(20)
        num_sections = struct.unpack_from("<H", coff, 2)[0]
        opt_header_size = struct.unpack_from("<H", coff, 16)[0]
        f.seek(pe_offset + 24 + opt_header_size)
        for i in range(num_sections):
            sec = f.read(40)
            name = sec[0:8].rstrip(b"\x00").decode("ascii", errors="replace")
            vsize = struct.unpack_from("<I", sec, 8)[0]
            rva = struct.unpack_from("<I", sec, 12)[0]
            raw_size = struct.unpack_from("<I", sec, 16)[0]
            raw_offset = struct.unpack_from("<I", sec, 20)[0]
            sections[name] = (rva, rva + vsize, raw_offset)
    return sections

def make_rva_to_file(sections):
    def rva_to_file(rva):
        for name, (start, end, file_base) in sections.items():
            if start <= rva < end:
                return file_base + (rva - start)
        return None
    return rva_to_file

IMAGE_BASE = 0x140000000

# Patch definitions: name -> (virtual_address, hex_bytes)
PATCHES_VA = {
    "GetLimit_ret1":             (0x140F2FC85, "6A FF 58 90 90"),
    "GetLimit_ret2":             (0x140F2FC95, "6A FF 58 90 90"),
    "TierLen_4to3":              (0x140F3137D, "48 C7 40 18 03 00 00 00"),
    "FreeStr_to_Pro":            (0x1418D15B8, "70 72 6F 00"),
    "QuotaLimit_init_neg1":      (0x140F2E007, "48 C7 40 50 FF FF FF FF"),
    "RefreshTier_noop":          (0x140F33080, "31 C0 31 DB C3 90 90 90 90"),
    "StartTierSync_noop":        (0x140F33EC0, "C3 90 90 90 90 90 90 90 90 90 90"),
}


def check(verbose=True):
    if not os.path.exists(TARGET):
        print(f"ERROR: {TARGET} not found")
        return False

    sections = parse_pe_sections(TARGET)
    rva_to_file = make_rva_to_file(sections)

    all_ok = True
    with open(TARGET, "rb") as f:
        for name, (va, hexdata) in PATCHES_VA.items():
            expected = bytes.fromhex(hexdata.replace(" ", ""))
            rva = va - IMAGE_BASE
            file_off = rva_to_file(rva)
            if file_off is None:
                if verbose:
                    print(f"  ? {name}: Cannot map VA 0x{va:X}")
                continue
            f.seek(file_off)
            actual = f.read(len(expected))
            if actual == expected:
                if verbose:
                    print(f"  [OK] {name} (file 0x{file_off:X})")
            else:
                all_ok = False
                if verbose:
                    print(f"  [FAIL] {name}: expected {expected.hex()}, got {actual.hex()}")

    if verbose:
        if all_ok:
            print("\nAll 7 patches applied!")
        else:
            print("\nSome patches are missing!")
    return all_ok


def apply():
    if not os.path.exists(TARGET):
        print(f"ERROR: {TARGET} not found")
        return 1

    sections = parse_pe_sections(TARGET)
    rva_to_file = make_rva_to_file(sections)

    if not os.path.exists(BACKUP):
        ans = input(f"Create backup {BACKUP}? [Y/n] ").strip().lower()
        if ans in ("", "y", "yes"):
            shutil.copy2(TARGET, BACKUP)
            print(f"Backup: {BACKUP}")
    else:
        print(f"Backup exists: {BACKUP}")

    with open(TARGET, "rb") as f:
        data = bytearray(f.read())

    print(f"\nPatching {TARGET} ({len(data):,} bytes)...\n")

    for name, (va, hexdata) in PATCHES_VA.items():
        patch_bytes = bytes.fromhex(hexdata.replace(" ", ""))
        rva = va - IMAGE_BASE
        file_off = rva_to_file(rva)
        if file_off is None:
            print(f"  [SKIP] {name}: Cannot map VA 0x{va:X}")
            continue
        old = data[file_off:file_off + len(patch_bytes)]
        data[file_off:file_off + len(patch_bytes)] = patch_bytes
        print(f"  [OK] {name}: 0x{file_off:X} {old.hex()} -> {patch_bytes.hex()}")

    with open(TARGET, "wb") as f:
        f.write(data)

    print(f"\nDone. {len(PATCHES_VA)} patches applied.")
    print(f"Backup: {BACKUP}")
    print("\nVerifying...")
    check()
    return 0


def restore():
    if not os.path.exists(BACKUP):
        print(f"ERROR: backup {BACKUP} not found")
        return 1
    print(f"Restoring {TARGET} from {BACKUP}...")
    shutil.copy2(BACKUP, TARGET)
    print("Restored.")
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "patch":
        return apply()
    elif cmd == "restore":
        return restore()
    elif cmd == "check":
        check()
        return 0
    else:
        print(f"Usage: {sys.argv[0]} [patch|restore|check]")
        print("\nPatches (v2.0):")
        for name, (va, hexdata) in PATCHES_VA.items():
            print(f"  {name}: VA 0x{va:X}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
