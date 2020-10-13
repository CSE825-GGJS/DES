from itertools import chain
from os import urandom
from typing import cast, List, Sequence, Tuple, Union

key_permutation = (
    57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18, 10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36, 63, 55,
    47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4
)

subkey_permutation = (
    14, 17, 11, 24, 1, 5, 3, 28, 15, 6, 21, 10, 23, 19, 12, 4, 26, 8, 16, 7, 27, 20, 13, 2, 41, 52, 31, 37, 47, 55, 30,
    40, 51, 45, 33, 48, 44, 49, 39, 56, 34, 53, 46, 42, 50, 36, 29, 32
)

cumulative_shifts = (1, 2, 4, 6, 8, 10, 12, 14, 15, 17, 19, 21, 23, 25, 27, 28)

data_permutation = (
    58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40, 32,
    24, 16, 8, 57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47,
    39, 31, 23, 15, 7
)

selection_table = (
    32, 1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 9, 8, 9, 10, 11, 12, 13, 12, 13, 14, 15, 16, 17, 16, 17, 18, 19, 20, 21, 20, 21,
    22, 23, 24, 25, 24, 25, 26, 27, 28, 29, 28, 29, 30, 31, 32, 1
)

s_block_final_permutation = (
    16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31, 10, 2, 8, 24, 14, 32, 27, 3, 9, 19, 13, 30, 6, 22, 11, 4,
    25
)

inverse_data_permutation = (
    40, 8, 48, 16, 56, 24, 64, 32, 39, 7, 47, 15, 55, 23, 63, 31, 38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21,
    61, 29, 36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27, 34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9,
    49, 17, 57, 25
)

s_box_table = (
    (
        (14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7),
        (0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8),
        (4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0),
        (15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13)
    ),
    (
        (15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10),
        (3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5),
        (0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15),
        (13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9)
    ),
    (
        (10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8),
        (13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1),
        (13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7),
        (1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12)
    ),
    (
        (7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15),
        (13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9),
        (10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4),
        (3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14)
    ),
    (
        (2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9),
        (14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6),
        (4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14),
        (11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3)
    ),
    (
        (12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11),
        (10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8),
        (9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6),
        (4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13)
    ),
    (
        (4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1),
        (13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6),
        (1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2),
        (6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12)
    ),
    (
        (13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7),
        (1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2),
        (7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8),
        (2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11)
    ),
)

# Constants section
ENCRYPT = 0
DECRYPT = 1

NONE_GIVEN = -1

ELECTRONIC_CODE_BOOK = 0b000
CIPHERBLOCK_CHAINING = 0b001
CIPHER_FEEDBACK = 0b010
OUTPUT_FEEDBACK = 0b011

TRIPLE = 0b100
NOT_TRIPLE_BITMASK = TRIPLE - 1

TRIPLE_ECB = TRIPLE | ELECTRONIC_CODE_BOOK
TRIPLE_CBC = TRIPLE | CIPHERBLOCK_CHAINING
TRIPLE_CFB = TRIPLE | CIPHER_FEEDBACK
TRIPLE_OFB = TRIPLE | OUTPUT_FEEDBACK


def int_to_bits(n: int, bit_length: int) -> Sequence[bool]:
    """Convert an integer to a sequence of big-endian bits.

    The bit length of your field must be given to get an output of the correct size.
    """
    padding = [False] * (bit_length - n.bit_length())
    if n == 0:
        return padding
    value = [x == '1' for x in bin(n)[2:]]
    ret = padding + value
    if len(ret) != bit_length:
        raise RuntimeError("Could not produce a valid bit sequence", n, bit_length, ret)
    return ret


def bits_to_int(block: Sequence[bool]) -> int:
    """Convert a sequence of big-endian bits to an integer."""
    return sum(x << idx for idx, x in enumerate(reversed(block)))
    # goes over each bit from least significant to most, then shifts their value out by their index


def circular_shift(n: int, i: int, bit_length: int) -> int:
    """Move the most significant i bits to the least significant end."""
    block = int_to_bits(n, bit_length)
    block = tuple(chain(block[i:], block[:i]))
    return bits_to_int(block)


def permute_int(n: int, table: Sequence[int], bit_length: int, offset: int = 1) -> int:
    """Mutate an integer based on a lookup table.

    Given an integer and a permutation table in the form 'the bit at this index becomes the bit at this value in the
    original', return a new integer. An offset parameter is provided in case the permutation table is not 1-indexed.
    """
    block = int_to_bits(n, bit_length)
    ret = tuple(block[x - offset] for x in table)
    return bits_to_int(ret)


def s_box(table: int, s: int) -> int:
    y = (s >> 1) % 16
    x = (s % 2) + ((s >> 5) << 1)
    # print(f"Looking up {table}, {x}, {y}")
    return s_box_table[table][x][y]


def f(r_block: int, subkey: int) -> int:
    e_block = permute_int(r_block, selection_table, 32)  # permute by the e-bit table (32b -> 48b)
    e_block ^= subkey  # XOR with subkey
    e_bitarray = int_to_bits(e_block, 48)  # convert to a bitarray to feed to S-Boxes
    s_boxes = [s_box(i, bits_to_int(e_bitarray[i * 6:(i + 1) * 6])) for i in range(48 // 6)]
    # split into 6-bit chunks and feed to s-boxes, getting 4-bit chunks in return
    e_block = bits_to_int(tuple(chain.from_iterable(int_to_bits(s, 4) for s in s_boxes)))
    # combine the bitarrays and read back as an int
    return permute_int(e_block, s_block_final_permutation, 32)  # feed the 8*4 = 32 bits into a permutation table


def shuffle(l_block: int, r_block: int, subkey: int) -> Tuple[int, int]:
    # L[n] = R[n-1]
    # R[n] = L[n-1] + f(R[n-1], K[n-1])
    # the key being a different index is because they indexed at 1 for some reason
    return r_block, (l_block ^ f(r_block, subkey))


class DESMachine:
    def __init__(
        self,
        key: Union[int, Sequence[int]],
        initialization_vector: int = 0,
        default_mode: int = ELECTRONIC_CODE_BOOK
    ):
        if not isinstance(key, int):
            keys = key
        else:
            keys = (key, key, key)
        if any(k.bit_length() > 64 for k in keys):
            raise ValueError("Key must be 64 bits or less")
        keys = tuple(permute_int(k, key_permutation, 64) for k in keys)  # spits out 56 bits
        keys_c = tuple(k >> 28 for k in keys)
        keys_d = tuple(k % (1 << 28) for k in keys)
        self.__subkeys = tuple(
            tuple(
                permute_int((circular_shift(key_c, x, 28) << 28) + circular_shift(key_d, x, 28), subkey_permutation, 56)
                for x in cumulative_shifts)
            for key_c, key_d in zip(keys_c, keys_d)
        )
        self.reset(initialization_vector=initialization_vector, default_mode=default_mode)

    def encrypt(self, *args, mode=NONE_GIVEN) -> bytes:
        return self.crypt_blocks(*args, action=ENCRYPT, mode=mode)

    def decrypt(self, *args, mode=NONE_GIVEN) -> bytes:
        return self.crypt_blocks(*args, action=DECRYPT, mode=mode)

    def reset(
        self,
        initialization_vector: Union[int, bytes, Sequence[Union[int, bytes]]] = (b'\00' * 8, ) * 3,
        default_mode: int = ELECTRONIC_CODE_BOOK
    ) -> None:
        if isinstance(initialization_vector, (int, bytes)):
            initialization_vector = [initialization_vector] * 3
        else:
            initialization_vector = list(initialization_vector)
        for idx, iv in enumerate(initialization_vector):
            if isinstance(iv, int):
                initialization_vector[idx] = iv.to_bytes(8, 'big')
        self.default_mode = default_mode
        self.last_block_encrypt: List[bytes] = cast(List[bytes], initialization_vector)
        self.last_block_decrypt: List[bytes] = cast(List[bytes], initialization_vector).copy()

    def crypt_block(
        self,
        block: bytes,
        action: int = ENCRYPT,
        mode: int = NONE_GIVEN,
        key_index: int = 0
    ) -> bytes:
        """Encrypts a block of up to 8 bytes in block cipher mode."""
        if action not in (ENCRYPT, DECRYPT):
            raise ValueError("Unknown action")

        if mode == NONE_GIVEN:
            mode = self.default_mode

        if mode >> 2:
            new_mode = mode & NOT_TRIPLE_BITMASK
            return self.crypt_block(
                self.crypt_block(
                    self.crypt_block(
                        block,
                        action=action,
                        mode=new_mode,
                        key_index=0
                    ),
                    action=not action,
                    mode=new_mode,
                    key_index=1
                ),
                action=action,
                mode=new_mode,
                key_index=2
            )

        if (mode & NOT_TRIPLE_BITMASK) in (CIPHER_FEEDBACK, OUTPUT_FEEDBACK):
            raise NotImplementedError()

        if len(block) != 8:  # then we need to pad this
            chars = 8 - len(block)
            return b'\00' * chars

        if (mode & NOT_TRIPLE_BITMASK) == CIPHERBLOCK_CHAINING:
            if action == ENCRYPT:
                block = bytes(x ^ y for x, y in zip(block, self.last_block_encrypt[key_index]))

        data = permute_int(int.from_bytes(block, 'big'), data_permutation, 64)
        l_block = data >> 32  # to get the most significant half, shift right
        r_block = data % (1 << 32)  # erase the left half
        for subkey in (self.__subkeys[key_index] if (action == ENCRYPT) else reversed(self.__subkeys[key_index])):
            l_block, r_block = shuffle(l_block, r_block, subkey)
        return_block = permute_int((r_block << 32) + l_block, inverse_data_permutation, 64).to_bytes(8, 'big')

        if (mode & NOT_TRIPLE_BITMASK) == CIPHERBLOCK_CHAINING:
            if action == ENCRYPT:
                self.last_block_encrypt[key_index] = return_block
            else:
                tmp = bytes(x ^ y for x, y in zip(return_block, self.last_block_decrypt[key_index]))
                self.last_block_decrypt[key_index] = block
                return tmp

        return return_block

    def pad_random(self, blocks: int) -> bytes:
        """Encrypt a block of random bytes."""
        return b''.join(self.crypt_block(urandom(8)) for _ in range(blocks))

    def crypt_blocks(self, *blocks: bytes, **kwargs) -> bytes:
        """Encrypt a group of up-to-8-byte blocks or a longer bytestream."""
        if len(blocks) == 1 and len(blocks[0]) > 8:
            blocks = tuple(blocks[0][x:8 + x] for x in range(0, len(blocks[0]), 8))
        return b''.join(self.crypt_block(block, **kwargs) for block in blocks)
