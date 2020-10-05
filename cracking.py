from multiprocessing import Pool
from pathlib import Path
from string import ascii_letters
from typing import Tuple

from des_ints import DESMachine

crypttext = (0b1010001011011101010000111110101101000010100011010100010000010011).to_bytes(8, 'big')
blocks = [crypttext[x:8+x] for x in range(0, len(crypttext), 8)]

wordlist = [word.lower() for word in Path('/usr/share/dict/words').read_text().splitlines() if len(word) > 1]


def process(key: int) -> Tuple[bool, bytes, int]:
    key <<= 48  # shift left 48 bits
    machine = DESMachine(key)
    plain_block_0 = machine.crypt_block(blocks[0], encrypt=False)
    try:
        string = plain_block_0.decode('ascii').lower()
    except Exception:
        return (False, plain_block_0, key)
    if any(char not in ascii_letters for char in string):
        return (False, plain_block_0, key)
    if any(word in string for word in wordlist):
        return (True, plain_block_0, key)
    return (False, plain_block_0, key)


def main():
    with Pool() as p:
        for plausibility, block, key in p.imap_unordered(process, range(1 << 16)):
            if plausibility:
                print(f"0x{key:016x} yields: {block}")
                tmp_machine = DESMachine(key)
                print(f"\tfull decryption yields: {tmp_machine.crypt_blocks(*blocks, encrypt=False)}")


if __name__ == '__main__':
    main()