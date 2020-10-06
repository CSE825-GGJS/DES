from multiprocessing import Pool
from pathlib import Path
from string import ascii_letters
from typing import Tuple

from des_ints import DESMachine

crypttext = bytes.fromhex("f45d1b8d606093949f8d09fcec9d4fa4650dd34dac6cd4c535aac237344a3edf74ef9392857285ba7198ca3a7e1bef5e338d0592417211eda0f3df2cea4d285d550b7baa0f63db6125823e3df164491b")
blocks = [crypttext[x:8+x] for x in range(0, len(crypttext), 8)]

wordlist = [word.lower() for word in Path('/usr/share/dict/words').read_text().splitlines() if len(word) > 1]
allowed_letters = set(ascii_letters.lower() + " ,.'\"_-")


def process(key: int) -> Tuple[bool, bytes, int]:
    key |= 0x0DEADBEEF0000000
    machine = DESMachine(key)
    plain_block_0 = machine.crypt_block(blocks[0], encrypt=False)
    try:
        string = plain_block_0.decode('ascii').lower()
    except Exception:
        return (False, plain_block_0, key)
    if any(char not in allowed_letters for char in string):
        return (False, plain_block_0, key)
    if any(word in string for word in wordlist):
        return (True, plain_block_0, key)
    return (False, plain_block_0, key)


def main():
    with Pool() as p:
        for plausibility, block, key in p.imap_unordered(process, range(1 << 24)):
            if plausibility:
                print(f"0x{key:016x} yields: {block}")
                tmp_machine = DESMachine(key)
                print(f"\tfull decryption yields: {tmp_machine.crypt_blocks(*blocks, encrypt=False)}")


if __name__ == '__main__':
    main()
