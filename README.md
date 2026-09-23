<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# Adventure UberGROM 8K

A finished Adventure cartridge by **hexbus**: load adventures from **ROM1**,
save progress to **UBE1**, and manage saved games from the cartridge menu.
UBE1 means UBergromEeprom1.

The DSR, file manager and BASIC CALL CAT occupy 8,167 bytes of one 8 KiB GROM,
including `2026 Hexbus`. The remaining 25 bytes are padding. The original
Adventure module and its small ROM1 loader occupy a separate GROM slot.

This repository freezes that runtime. ToD, printer and cassette redirection
belong to separate development work and are not features of this release.

## Supply your own adventures

No adventure databases, original Adventure module, or AVR firmware are bundled.
The [build guide](docs/building.md) has WHTech links and a short file-list example.
Python builds your own 512 KiB ROM and complete ATmega programming images using
the frozen components in [release](release/).

- [Build with your own files](docs/building.md)
- [Use and program the cartridge](docs/programming.md)
- [How the code works](docs/code-guide.md)
- [Freeze and verification](docs/verification.md)

The included 8 KiB GROM is our service alone, **not** a full ATmega image.
The included EEPROM is blank; retain existing saves before reprogramming.

## Credits

Project by **hexbus**: [GitHub](https://github.com/hexbus) and
[www.hexbus.com](https://www.hexbus.com).
Thanks to **Mike Brent (Tursi)** for UberGROM and his mapping advice, and
**Fred** for the original ROM disk discussions. Original authors retain their
credits; see [NOTICE.txt](NOTICE.txt).

Original code is **Apache 2.0**; documentation is **CC BY 4.0**.
Both preserve applicable attribution when redistributed. [License details](LICENSE.md).
Please keep the embedded `2026 Hexbus` signature when reusing the UBE1 GROM.

This is a local release preparation. No GitHub repository has been created
or published. `github-release/` is an export made by `tools/prepare_release.py`;
private inputs and historical cartridge images are excluded.
