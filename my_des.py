"""DES algorithm implementation
Gabe Appleton, Shashank Mohan, Gregory Hess, and Julia Zheng
"""
def bit_array_to_string(bitarray): 
    chars = []
    for b in range(len(bitarray) // 8):
        byte = bitarray[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)
   
def split_list(list, n_partition):
    return [list[k:k+n_partition] for k in range(0, len(list), n_partition)]
    
def get_binary_value(val, bitsize): #Return the binary value as a string of the given size 
    my_binary = bin(val)[2:] if isinstance(val, int) else bin(ord(val))[2:]
    while len(my_binary) < bitsize:
        my_binary = "0"+my_binary #Add as many 0 as needed to get the wanted size
    return my_binary

def hex_string_to_bit_array(data_text):
    bitarray = list()
    for char in data_text:
        binary = get_binary_value(char, 8)
        bitarray.extend([int(x) for x in list(binary)]) 
    print(data_text)
    print(''.join(map(str, bitarray)))
    return bitarray

shift_per_round = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]
first_key_permut_table = [57, 49, 41, 33, 25, 17, 9,
                            1, 58, 50, 42, 34, 26, 18,
                            10, 2, 59, 51, 43, 35, 27,
                            19, 11, 3, 60, 52, 44, 36,
                            63, 55, 47, 39, 31, 23, 15,
                            7, 62, 54, 46, 38, 30, 22,
                            14, 6, 61, 53, 45, 37, 29,
                            21, 13, 5, 28, 20, 12, 4]

subkey_permut_table = [14, 17, 11, 24, 1, 5, 3, 28,
                        15, 6, 21, 10, 23, 19, 12, 4,
                        26, 8, 16, 7, 27, 20, 13, 2,
                        41, 52, 31, 37, 47, 55, 30, 40,
                        51, 45, 33, 48, 44, 49, 39, 56,
                        34, 53, 46, 42, 50, 36, 29, 32]

s_box_table = [[[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
                 [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
                 [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
                 [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],],

                [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
                 [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
                 [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
                 [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],],

                [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
                 [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
                 [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
                 [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],],

                [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
                 [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
                 [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
                 [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],],  

                [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
                 [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
                 [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
                 [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],], 

                [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
                 [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
                 [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
                 [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],], 

                [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
                 [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
                 [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
                 [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],],
                   
                [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
                 [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
                 [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
                 [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11], ] ]

s_block_final_permut = [16, 7, 20, 21, 29, 12, 28, 17,
                         1, 15, 23, 26, 5, 18, 31, 10,
                         2, 8, 24, 14, 32, 27, 3, 9,
                         19, 13, 30, 6, 22, 11, 4, 25]
                         

first_data_permut_table = [58, 50, 42, 34, 26, 18, 10, 2,
                          60, 52, 44, 36, 28, 20, 12, 4,
                          62, 54, 46, 38, 30, 22, 14, 6,
                          64, 56, 48, 40, 32, 24, 16, 8,
                          57, 49, 41, 33, 25, 17, 9, 1,
                          59, 51, 43, 35, 27, 19, 11, 3,
                          61, 53, 45, 37, 29, 21, 13, 5,
                          63, 55, 47, 39, 31, 23, 15, 7]
                          
inverse_data_permutation = [40, 8, 48, 16, 56, 24, 64, 32,
                            39, 7, 47, 15, 55, 23, 63, 31,
                            38, 6, 46, 14, 54, 22, 62, 30,
                            37, 5, 45, 13, 53, 21, 61, 29,
                            36, 4, 44, 12, 52, 20, 60, 28,
                            35, 3, 43, 11, 51, 19, 59, 27,
                            34, 2, 42, 10, 50, 18, 58, 26,
                            33, 1, 41, 9, 49, 17, 57, 25]

#for applying XOR 
selection_table = [32, 1, 2, 3, 4, 5,
                     4, 5, 6, 7, 8, 9,
                     8, 9, 10, 11, 12, 13,
                     12, 13, 14, 15, 16, 17,
                     16, 17, 18, 19, 20, 21,
                     20, 21, 22, 23, 24, 25,
                     24, 25, 26, 27, 28, 29,
                     28, 29, 30, 31, 32, 1]

   
class des():
    def __init__(self):
        self.key = None
        self.data_text = None
        self.keys = list()

    def encrypt(self, key, data_text, added_padding=False):
        if len(key) > 8:
            key = key[:8] #trim key to 8 bytes
        self.key = key
        self.data_text = data_text
        if added_padding:
            self.padding_random()
        self.generatekeys()
        text_blocks = split_list(self.data_text, 8) 
        result = list()
        for block in text_blocks:#Loop over all the blocks of data
            block = hex_string_to_bit_array(block)#make block a bitarray
            block = self.permut(block,first_data_permut_table)#first permutation
            left_subkey, right_subkey = split_list(block, 32) #left_subkey, right_subkey
            temp = None
            for i in range(16): 
                temp_right_subkey = self.expand(right_subkey, selection_table) 
                temp = self.xor(self.keys[i], temp_right_subkey)
                temp = self.substitute(temp) 
                temp = self.permut(temp, s_block_final_permut)
                temp = self.xor(left_subkey, temp)
                left_subkey = right_subkey
                right_subkey = temp
            result += self.permut(right_subkey+left_subkey, inverse_data_permutation) 
        final_res = bit_array_to_string(result)
        return final_res 
    
    def decrypt(self, key, data_text, added_padding=False):
        if len(key) > 8:
            key = key[:8] 
        self.key = key
        self.data_text = data_text
        self.generatekeys() 
        text_blocks = split_list(self.data_text, 8) 
        result = list()
        for block in text_blocks:
            block = hex_string_to_bit_array(block)
            block = self.permut(block,first_data_permut_table)
            left_subkey, right_subkey = split_list(block, 32) 
            temp = None
            for i in range(16): 
                temp_right_subkey = self.expand(right_subkey, selection_table) 
                temp = self.xor(self.keys[15-i], temp_right_subkey)
                temp = self.substitute(temp) 
                temp = self.permut(temp, s_block_final_permut)
                temp = self.xor(left_subkey, temp)
                left_subkey = right_subkey
                right_subkey = temp
            result += self.permut(right_subkey+left_subkey, inverse_data_permutation) 
        final_res = bit_array_to_string(result)
        if added_padding:
            return self.removePadding(final_res) 
        else:
            return final_res 

   
    def substitute(self, temp_subkey):
        sub_block = split_list(temp_subkey, 6)
        result = list()
        for i in range(len(sub_block)):
            block = sub_block[i]
            row = int(str(block[0])+str(block[5]),2)
            column = int(''.join([str(x) for x in block[1:][:-1]]),2) 
            temp = s_box_table[i][row][column] 
            binary = get_binary_value(temp, 4)
            result += [int(x) for x in binary]
        return result

    def padding_random(self):
        pad_len = 8 - (len(self.data_text) % 8)
        self.data_text += pad_len * chr(pad_len)
   
    def generatekeys(self):
        self.keys = []
        key = hex_string_to_bit_array(self.key)
        key = self.permut(key, first_key_permut_table) 
        left_subkey, right_subkey = split_list(key, 28) 
        for i in range(16):
            left_subkey, right_subkey = self.circular_shift(left_subkey, right_subkey, shift_per_round[i]) 
            temp = left_subkey + right_subkey 
            self.keys.append(self.permut(temp, subkey_permut_table)) 
    def permut(self, block, table):
        return [block[x-1] for x in table]
    
    def circular_shift(self, left_subkey, right_subkey, n_partition): 
        return left_subkey[n_partition:] + left_subkey[:n_partition], right_subkey[n_partition:] + right_subkey[:n_partition]
    
    def removePadding(self, data):
        pad_len = ord(data[-1])
        return data[:-pad_len]

    def expand(self, block, table):
        return [block[x-1] for x in table]
    
    def xor(self, t1, t2):
        return [x^y for x,y in zip(t1,t2)]
if __name__ == '__main__':
    key = bytearray.fromhex("133457799BBCDFF1")
    data_text= bytearray.fromhex("0123456789ABCDEF")
    right_subkey = des()
    ciphered = right_subkey.encrypt(key,data_text)
    decrypted = right_subkey.decrypt(key,ciphered)
    print("Ciphered: " +" ".join(hex(ord(x))[2:].zfill(2) for x in ciphered))
    print("Deciphered: "+ " ".join(hex(ord(x))[2:].zfill(2) for x in decrypted))
    if "".join(hex(ord(x))[2:].zfill(2) for x in ciphered) == ''.join('{:02x}'.format(x) for x in bytearray.fromhex("85E813540F0AB405")):
        print("WOOT YOU MATCH YAY GOOD JOB")
    else:
        print( ' '.join('{:02x}'.format(x) for x in bytearray.fromhex("85E813540F0AB405")))
        print("".join(hex(ord(x))[2:].zfill(2) for x in ciphered))