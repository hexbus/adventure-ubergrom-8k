<!-- Copyright (c) 2026 hexbus. SPDX-License-Identifier: CC-BY-4.0 -->

# Adventure UberGROM 8K for the TI-99/4A

I wanted to put the adventures and a small place to save games inside the
cartridge. Pick an adventure, play it, save it, and come back to it later -
without needing a disk system or cassette recorder.

That's what this does. **ROM1** holds the adventures, and **UBE1** holds your
saved games. UBE1 stands for **UBergromEeprom1**. There's a **SAVED GAMES** item
on the cartridge menu, and TI BASIC can catalog and delete files too.

We kept the DSR, file manager and BASIC CALL CAT together in one 8K GROM.
They use 8,167 bytes, including the little `2026 Hexbus` signature. That leaves
25 bytes. The original Adventure GROM and the ROM1 loader are in another slot.

This is the version we're freezing. Tunnels of Doom and the printer/cassette
ideas are still on the backlog, but they'll be worked on separately.

## Put your own adventures in it

The adventure files aren't included here. You'll also need the original
Adventure GROM and Tursi's UberGROM firmware. The [build directions](docs/building.md)
have the WHTech links and show how to make your own list of adventures.

The builder makes a 512K adventure ROM and the ATmega programming files using
our finished components in [release](release/).

- [Build it with your adventures](docs/building.md)
- [Program the cartridge, play and save](docs/programming.md)
- [What's going on in the code](docs/code-guide.md)
- [What we froze and checked](docs/verification.md)

The 8K GROM in `release/` is just our DSR and menu. It isn't a complete ATmega
image. The EEPROM file starts with an empty save area, so back up your existing
EEPROM before programming over a cartridge you've been using.

## Thanks and credits

Thanks to **Tursi (Mike Brent)** for UberGROM, the firmware and documentation,
and for pointing out the mapping that gets rid of REVIEW MODULE LIBRARY.
Thanks to **Fred** for the original ROM disk discussions.

This project is by **hexbus**. You can find my other stuff on
[GitHub](https://github.com/hexbus) and at [www.hexbus.com](https://www.hexbus.com).
The original authors keep their credits - see [NOTICE.txt](NOTICE.txt).

The code is **Apache 2.0** and the documentation is **CC BY 4.0**.
See the [license details](LICENSE.md). If you use the UBE1 GROM in something
else, I ask that you keep the `2026 Hexbus` signature in it so people know
where it came from.
