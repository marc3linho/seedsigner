#
# bytewords.py
#
# Copyright © 2020 Foundation Devices, Inc.
# Licensed under the "BSD-2-Clause Plus Patent License"
#

from .utils import crc32_bytes, partition

BYTEWORDS = 'ableacidalsoapexaquaarchatomauntawayaxisbackbaldbarnbeltbetabiasbluebodybragbrewbulbbuzzcalmcashcatschefcityclawcodecolacookcostcruxcurlcuspcyandarkdatadaysdelidicedietdoordowndrawdropdrumdulldutyeacheasyechoedgeepicevenexamexiteyesfactfairfernfigsfilmfishfizzflapflewfluxfoxyfreefrogfuelfundgalagamegeargemsgiftgirlglowgoodgraygrimgurugushgyrohalfhanghardhawkheathelphighhillholyhopehornhutsicedideaidleinchinkyintoirisironitemjadejazzjoinjoltjowljudojugsjumpjunkjurykeepkenokeptkeyskickkilnkingkitekiwiknoblamblavalazyleaflegsliarlimplionlistlogoloudloveluaulucklungmainmanymathmazememomenumeowmildmintmissmonknailnavyneednewsnextnoonnotenumbobeyoboeomitonyxopenovalowlspaidpartpeckplaypluspoempoolposepuffpumapurrquadquizraceramprealredorichroadrockroofrubyruinrunsrustsafesagascarsetssilkskewslotsoapsolosongstubsurfswantacotasktaxitenttiedtimetinytoiltombtoystriptunatwinuglyundouniturgeuservastveryvetovialvibeviewvisavoidvowswallwandwarmwaspwavewaxywebswhatwhenwhizwolfworkyankyawnyellyogayurtzapszerozestzinczonezoom'
WORD_ARRAY = None

def decode_word(word, word_len):
    global WORD_ARRAY
    global BYTEWORDS

    if len(word) != word_len:
        raise ValueError('Invalid Bytewords.')

    dim = 26

    # Since the first and last letters of each Byteword are unique,
    # we can use them as indexes into a two-dimensional lookup table.
    # This table is generated lazily.
    if WORD_ARRAY == None:
        WORD_ARRAY = [-1] * (dim * dim)  # create empty array

        for i in range(256):
            byteword_offset = i * 4
            x = ord(BYTEWORDS[byteword_offset]) - ord('a')
            y = ord(BYTEWORDS[byteword_offset + 3]) - ord('a')
            array_offset = y * dim + x
            WORD_ARRAY[array_offset] = i

    # If the coordinates generated by the first and last letters are out of bounds,
    # or the lookup table contains -1 at the coordinates, then the word is not valid.
    x = ord(word[0].lower()) - ord('a')
    y = ord((word[3 if len(word) == 4 else 1]).lower()) - ord('a')
    if not (0 <= x and x < dim and 0 <= y and y < dim):
        raise ValueError('Invalid Bytewords.')

    offset = y * dim + x
    value = WORD_ARRAY[offset]
    if value == -1:
        raise ValueError('Invalid Bytewords.')

    # If we're decoding a full four-letter word, verify that the two middle letters are correct.
    if len(word) == 4:
        byteword_offset = value * 4
        c1 = word[1].lower()
        c2 = word[2].lower()
        if c1 != BYTEWORDS[byteword_offset + 1] or c2 != BYTEWORDS[byteword_offset + 2]:
            raise ValueError('Invalid Bytewords.')

    # Successful decode.
    return value

def get_word(index):
    byteword_offset = index * 4
    return BYTEWORDS[byteword_offset:byteword_offset + 4]

def get_minimal_word(index):
    byteword_offset = index * 4
    return BYTEWORDS[byteword_offset] + BYTEWORDS[byteword_offset + 3]

def encode(buf, separator):
    words = []
    for i in range(len(buf)):
        byte = buf[i]
        words.append(get_word(byte))

    return separator.join(words)

def add_crc(buf):
    crc_buf = crc32_bytes(buf)
    return buf + crc_buf

def encode_with_separator(buf, separator):
    crc_buf = add_crc(buf)
    return encode(crc_buf, separator)

def encode_minimal(buf):
    result = ''

    crc_buf = add_crc(buf)
    for i in range(len(crc_buf)):
        byte = crc_buf[i]
        result += get_minimal_word(byte)

    return result

def decode(s, separator, word_len):
    buf = bytearray()

    if word_len == 4:
        words = s.split(separator)
    else:
        words = partition(s, 2)

    for word in words:
        buf.append(decode_word(word, word_len))

    if len(buf) < 5:
        raise ValueError('Invalid Bytewords.') 

    # Validate checksum
    body = buf[0:-4]
    body_checksum = buf[-4:]
    checksum = crc32_bytes(body)
    # if checksum != body_checksum:
    #     raise ValueError('Invalid Bytewords.')

    return body

Bytewords_Style_standard = 1
Bytewords_Style_uri = 2
Bytewords_Style_minimal = 3

class Bytewords:
    @staticmethod
    def encode(style, bytes):
        if style == Bytewords_Style_standard:
            return encode_with_separator(bytes, ' ')
        elif style == Bytewords_Style_uri:
            return encode_with_separator(bytes, '-')
        elif style == Bytewords_Style_minimal:
            return encode_minimal(bytes)
        else:
            assert(False)

    @staticmethod
    def decode(style, str):
        if style == Bytewords_Style_standard:
            return decode(str, ' ', 4)
        elif style == Bytewords_Style_uri:
            return decode(str, '-', 4)
        elif style == Bytewords_Style_minimal:
            return decode(str, 0, 2)
        else:
            assert(False)
