#!/usr/bin/python3
# -*- coding: utf8 -*-
# 
# converts hp15c program into hp42s program
#
# !! ATTENTION - hp15c opcodes not fully implemented!!
#
# HowTo
# - import Listing into HP-15C emulator: https://hp-15c.homepage.t-online.de/homepage.htm
# - export listing as 15c txt file (UTF-16)
# - run conversion: ./conv15to42s.py file.15c > file.42s
# - check result: Might needs some manual adjustments. You night also want to change the label names
# - convert to raw: https://thomasokken.com/free42/download/unsupported/txt2raw/
#     ./txt2raw.pl file.42s
# - import into Free42/Plus42/DM42

# conversion into raw could also be done with the DM42 online tool
#  https://technical.swissmicros.com/decoders/dm42/
#  some codes are different to txt2raw. Check the online instruction for more
#  e.g.
#    txt2raw  |  dm42 decoder
#    ---------|--------------
#    CL\Sigma |  CL\GS
#    \Sigma+  |  \GS+
#    \Sigma-  |  \GS-
#    ->DEG    |  \->DEG
#
#--------------------------------------------------------------------------

import sys
import codecs
import chardet
import re

INFILE = 'sum.15c'

DBMAP = False
DBDGI = False
SRC   = False

#--------------------------------------------------------------------------

def decode_utf16le(infile):
    # read in binary mode
    encoded_text = open(infile, 'rb').read()

    bom = codecs.BOM_UTF16_LE
    assert encoded_text.startswith(bom)
    encoded_text = encoded_text[len(bom):]

    decoded_text = encoded_text.decode('utf-16le')

    #print(decoded_text)
    return decoded_text


def decode_utf8(infile):
    # read in binary mode
    encoded_text = open(infile, 'rb').read()

    decoded_text = encoded_text.decode('utf-8')

    #print(decoded_text)
    return decoded_text


def decode_iso8859_1(infile):
    # read in binary mode
    encoded_text = open(infile, 'rb').read()

    decoded_text = encoded_text.decode('iso-8859-1')

    #print(decoded_text)
    return decoded_text


def check_encoding(infile):
    # read in binary mode
    encoded_text = open(infile, 'rb').read()
    e_det  = chardet.detect(encoded_text)['encoding']
    e_conf = chardet.detect(encoded_text)['confidence']
    #print("%s: %s encoding with confidence %s" % (infile,e_det, e_conf))

    return e_det


def decode_file(infile, encoding):
    text = ''

    if encoding == 'UTF-16':
        text = decode_utf16le(infile)

    elif encoding == 'utf-8':
        text = decode_utf8(infile)

    elif encoding == 'ISO-8859-1':
        text = decode_iso8859_1(infile)
    else:
        print("no decoding function for codec '%s'" % encoding)

    #print(text)
    return text


ops = {
'÷': '/',
'×': 'x',
'-': '-',
'−': '-',
'+': '+'
}

codemapping = {
'÷': '/',
'-': '-',
'+': '+',
'−': '-',
'✛': '+',
'.': '.',
'%': '%',
'??': '??',
'∑': 'SUM',
'∑−': '∑−',
'0': '0',
'10ˣ': '10^X',
'10^x': '10^X',
'1/x': '1/X',
'1': '1',
'2': '2',
'3': '3',
'4': '4',
'5': '5',
'6': '6',
'7': '7',
'8': '8',
'9': '9',
'ABS': 'ABS',
'CF': 'CF',
'CHS': '+/-',
'?': 'CL\Sigma',
'CLx': 'CLX',
'COS-¹': 'ACOS',
'COS⁻¹': 'ACOS',
'COS?¹': 'ACOS',
'COS': 'COS',
'Cy,x': 'COMB',
'→DEG': '->DEG',
'DEG': 'DEG',
'DIM': 'DIM',
'DSE': 'DSE',
'e?': 'E^X',
'eˣ': 'E^X',
'EEX': 'E',
'ENG': 'ENG',
'ENTER': 'ENTER',
'ℯˣ': 'E^X',
'e^x': 'E^X',
'F?': 'FS?',
'FIX': 'FIX',
'FRAC': 'FP',
'GRD': 'GRAD',
'GSB': 'XEQ',
'GTO': 'GTO',
'→H': '->HR',
'→H.MS': '->HMS',
'HYP⁻¹': 'HYP',
'I': 'COMPLEX',
'INT': 'IP',
'ISG': 'ISG',
'LBL': 'LBL',
'LN': 'LN',
'LOG': 'LOG',
'L.R.': 'YINT',
'LST?': 'LASTX',
'LSTx': 'LASTX',
'LSTΧ': 'LASTX',
'MATRIX': 'NEWMAT',
'P': 'P',
'→P': '->POL',
'PSE': 'PSE',
'→RAD': '->RAD',
'RAD': 'RAD',
'RAN?#': 'RAN',
'RAN': 'RAN',
'RAN#': 'RAN',
'RCL': 'RCL',
'?,r': 'CORR',
'REG': 'CLRG',
'Re?Im': 'COMPLEX',
'Re↔Im': 'COMPLEX',
'RND': 'RND',
'R↓': 'Rv',
'R⬇': 'Rv',
'R⬆': 'R^',
'→R': '->REC',
'R/S': 'STOP',
'RTN': 'RTN',
'SCI': 'SCI',
'SF': 'SF',
'?+': '\Sigma+',
'∑+': '\Sigma+',
'SIN?¹': 'ASIN',
'SIN⁻¹': 'ASIN',
'SIN': 'SIN',
'SOLVE': 'SOLVE',
's': 'SDEV',
'STO': 'STO',
'TAN-¹': 'ATAN',
'TAN⁻¹': 'ATAN',
'TAN': 'TAN',
'TEST': 'TEST',
'×': 'x',
'✕': 'x',
'x≠0': 'X!=0',
'x<0': 'X<0',
'x≤0': 'X<=0',
'x=0': 'X=0?',
'x≥0': 'X>=0',
'x>0': 'X>0',
'x²': 'X^2',
'?x?': 'SQRT',
'√x': 'SQRT',
'√x̅': 'SQRT',
'x̅': 'MEAN',
'∫xy': 'PGMINT',
'Py,x': 'PERM',
'x<y': 'X<Y',
'x≤y': 'X<=Y?',
'x=y': 'X=Y',
'x≠y': 'X!=Y',
'x≥y': 'X>=Y',
'x>y': 'X>Y',
'x?y': 'X<>Y',
'x↔y': 'X<>Y',
'ŷ,r': 'CORR',
'y^x': 'Y^X',
'y?': 'Y^X',
'yˣ': 'Y^X',
'Δ%': '%CH',
'π': 'PI',
'Χ↔': 'X<>',
'Χ': 'Χ',
'Χ !': 'N!',
'Χ!': 'N!',
}

def convert2hp42s(text):
    # 000 {             }
    # 001 {    42 21 11 } f LBL A
    # 002 {           5 } 5
    # 003 {           1 } 1
    # 004 {    42 23 24 } f DIM (i)

    del_leading = re.compile(r'!^#|!^ ')
    get_line = re.compile(r'^\d{3} {.*} (.*)$')

    op_reg   = re.compile(r'(STO|RCL|LBL|GSB|GTO|FIX|SCI|ENG|DIM|ISG|DSE|F\?|SF|CF|MATRIX)')
    op_alpha = re.compile(r'(A|B|C|D|E|I)')
    op_num1  = re.compile(r'([0-9])')
    op_num2  = re.compile(r'\.([0-9])')
    op_digit = re.compile(r'(^[0-9.]$)')
    op_trig  = re.compile(r'(SIN|COS|TAN)')


    atxt = text.split('\n')
    DIGIT = False
    LAST_CHAR_DIGIT = False
    EEX_CHAR = False
    num_joined = ''

    for n in atxt:
        res = get_line.match(n.strip())
        if res:
            c  = res.group(1).split()
            ll = len(c)

            if SRC:
                print("_src: %s: %s" % (ll,c))

            # join single digits
            res2 = op_digit.match(c[0])
            if res2:
                DIGIT = True
                LAST_CHAR_DIGIT = True
                if (c[0] == '.') and (num_joined == ''):
                    num_joined = '0' + c[0]
                else:
                    num_joined = num_joined + c[0]

                if DBDGI:
                    print("_chr: digit: %s => %s" % (c[0],num_joined))

            elif (c[0] == 'EEX') and LAST_CHAR_DIGIT:
                DIGIT = True
                LAST_CHAR_DIGIT = True
                num_joined = num_joined + 'E'
                EEX_CHAR = True
                if DBDGI:
                    print("_eex: digit: %s => %s" % (c[0],num_joined))

            elif (c[0] == 'EEX') and not LAST_CHAR_DIGIT:
                DIGIT = True
                LAST_CHAR_DIGIT = True
                if (c[0] == 'EEX') and (num_joined == ''):
                    num_joined = '1' + 'E'
                EEX_CHAR = True
                if DBDGI:
                    print("_eex: digit: %s => %s" % (c[0],num_joined))

            elif (c[0] == 'CHS') and EEX_CHAR:
                DIGIT = True
                LAST_CHAR_DIGIT = True
                exp = re.split(r'([^0-9-])',num_joined)


                lexp = len(exp)
                if lexp == 3:
                    num_joined = exp[0]+exp[1]+'-'+exp[2]
                else:
                    if DBDGI:
                        print("exp is too small: %s" % exp)
                        print("num_joined      : %s" % num_joined)
                        print("EEX_CHAR        : %s" % EEX_CHAR)
                        print("DIGIT           : %s" % DIGIT)
                        print("LAST_CHAR_DIGIT : %s" % LAST_CHAR_DIGIT)

                if DBDGI:
                    print("_chs: digit: %s => %s ## %s " % (c[0],num_joined,exp))

            else:
                if DBDGI:
                    print("_end: set flages false")
                DIGIT = False
                EEX_CHAR = False

            #print("DIGIT           : %s" % DIGIT)
            #print("LAST_CHAR_DIGIT : %s" % LAST_CHAR_DIGIT)

            # print number
            if LAST_CHAR_DIGIT and not DIGIT:
                print("%s" % (num_joined))
                LAST_CHAR_DIGIT = False
                num_joined = ''

            if ll == 1:
                # _src: ['1']
                if c[0] in codemapping:
                    cmap = codemapping[c[0]]

                    if not LAST_CHAR_DIGIT:
                        print("%s" % (codemapping[c[0]]))
                else:
                    print("_uma1: '%s': '%s'," % (c[0], c[0]))


            elif (ll == 2) and ((c[0] == 'f') or (c[0] == 'g')):
                # _src: ['f', 'REG']
                if c[1] in codemapping:
                    print("%s" % (codemapping[c[1]]))

                else:
                    print("_uma2: '%s': '%s'," % (c[1], c[1]))

            elif (ll == 2) and ((c[0] != 'f') or (c[0] != 'g')):
                # _src: ['STO', 'I']
                if c[0] in codemapping:
                    #print("'%s': '%s'," % (c[0], codemapping[c[0]]))

                    res1 = op_reg.match(c[0])
                    if res1:

                        if op_alpha.match(c[1]):
                            par1 = op_alpha.sub(r'"\1"', c[1])
                            print("%s %s" % (codemapping[res1.group(1)],par1))

                        elif op_num1.match(c[1]):
                            par1 = op_num1.sub(r'0\1', c[1])
                            print("%s %s" % (codemapping[res1.group(1)],par1))

                        elif op_num2.match(c[1]):
                            par1 = op_num2.sub(r'1\1', c[1])
                            print("%s %s" % (codemapping[res1.group(1)],par1))

                        elif (c[1] == '(i)'):
                            print("%s %s" % (codemapping[res1.group(1)],'IND "I"'))

                    else:
                        print("## %s not matched2" % c[0])

                else:
                    print("_uma2: '%s': '%s'," % (c[0], c[0]))

            elif (ll == 3) and ((c[0] == 'f') or (c[0] == 'g')):
                # _src: ['f', 'LBL', 'A']
                # _src: ['f', '→', 'R']
                # _src: 3: ['f', 'Χ↔', '(i)']
                if c[1] in codemapping:
                    if DBMAP:
                        print("_map3: '%s': '%s'," % (c[1], codemapping[c[1]]))

                    res1 = op_reg.match(c[1])
                    if res1:

                        if op_alpha.match(c[2]):
                            par1 = op_alpha.sub(r'"\1"', c[2])
                            if ((c[1] == 'SF') or (c[1] == 'CF') or c[1] == 'FIX') and (c[2] == 'I'):
                                print("%s %s %s" % (codemapping[res1.group(1)],'IND',par1))
                            else:
                                print("%s %s" % (codemapping[res1.group(1)],par1))

                        elif op_num1.match(c[2]):
                            if (c[1] == 'MATRIX'):
                                # doesn't produce working program
                                if (c[2]) == '0':
                                    # delete matrix
                                    #print("%s" % ('MAT_0_DELETE'))
                                    print("%s" % ('STOP'))
                                elif (c[2]) == '1':
                                    # set position to 1,1
                                    print("%s" % ('1'))
                                    print("%s" % ('ENTER'))
                                    print("%s" % ('STOIJ'))
                                    print("%s" % ('RCLIJ'))
                                elif (c[2]) == '2':
                                    # transform Z^p into Z~
                                    #print("%s" % ('MAT_2_TRANS_ZP'))
                                    print("%s" % ('STOP'))
                                elif (c[2]) == '3':
                                    # transform Z~ into Z^p
                                    #print("%s" % ('MAT_3_TRANS_ZP'))
                                    print("%s" % ('STOP'))
                                elif (c[2]) == '4':
                                    # descriptor of transpose
                                    print("%s" % ('TRAN'))
                                elif (c[2]) == '5':
                                    # multiplies transpose
                                    print("%s" % ('TRAN'))
                                    print("%s" % ('x'))
                                elif (c[2]) == '6':
                                    # residual
                                    #print("%s" % ('MAT_6_RESIDUUM'))
                                    print("%s" % ('STOP'))
                                elif (c[2]) == '7':
                                    # row norm
                                    print("%s" % ('RNRM'))
                                elif (c[2]) == '8':
                                    # frobenius or euclidean norm
                                    print("%s" % ('FNRM'))
                                elif (c[2]) == '9':
                                    # determinant
                                    print("%s" % ('DET'))
                                else:
                                    print("%s" % ('MAT_UNKNOWN'))

                            elif ((c[1] == 'SF') and (c[2] == '9')):
                                print("%s" % ('BEEP'))

                            else:
                                par1 = op_num1.sub(r'0\1', c[2])
                                print("%s %s" % (codemapping[res1.group(1)],par1))

                        elif op_num2.match(c[2]):
                            par1 = op_num2.sub(r'1\1', c[2])
                            print("%s %s" % (codemapping[res1.group(1)],par1))

                        elif (c[2] == '(i)'):
                            print("%s %s" % (codemapping[res1.group(1)],'IND "I"'))

                        elif c[1] == 'TEST':
                            print("%s?" % (codemapping[c[2]]))
                        else:
                            print("## %s not matched3f1" % c[2])


                    elif c[1] == 'RAN':
                        print("%s" % (codemapping[c[1]]))

                    elif c[1] == 'TEST':
                        if c[2] in codemapping:
                            print("%s?" % (codemapping[c[2]]))
                        else:
                            print("## %s not matched3f2" % c[2])

                    elif c[1] == 'Χ↔':

                        if op_alpha.match(c[2]):
                            par1 = op_alpha.sub(r'"\1"', c[2])
                            print("%s %s" % (codemapping[c[1]],par1))

                        elif op_num1.match(c[2]):
                            par1 = op_num1.sub(r'0\1', c[2])
                            print("%s %s" % (codemapping[c[1]],par1))

                        elif op_num2.match(c[2]):
                            par1 = op_num2.sub(r'1\1', c[2])
                            print("%s %s" % (codemapping[c[1]],par1))

                        elif (c[2] == '(i)'):
                            print("%s %s" % (codemapping[c[1]],'IND "I"'))

                    elif ((c[1] == 'Χ') and (c[2] == '!')):
                        # _src: 3: ['f', 'Χ', '!']
                        c12 = c[1]+c[2]
                        if c12 in codemapping:
                            print("%s" % (codemapping[c12]))
                        else:
                            print("## %s not matched3f3a" % c12)

                    elif ((c[1] == 'P') and (c[2] == 'y,x')):
                        # _src: 3: ['f', 'P', 'y,x']
                        c12 = c[1]+c[2]
                        if c12 in codemapping:
                            print("%s" % (codemapping[c12]))
                        else:
                            print("## %s not matched3f3b" % c12)

                    elif ((c[1] == '∫xy') or (c[1] == 'SOLVE')):
                        # _src: 3: ['f', '∫xy', '3']
                        # _src: 3: ['f', 'SOLVE', '4']
                        # needs quoting
                        if op_alpha.match(c[2]):
                            par1 = op_alpha.sub(r'"\1"', c[2])
                            print("%s %s" % (codemapping[c[1]],par1))

                        elif op_num1.match(c[2]):
                            par1 = op_num1.sub(r'"0\1"', c[2])
                            print("%s %s" % (codemapping[c[1]],par1))

                        elif op_num2.match(c[2]):
                            par1 = op_num2.sub(r'"1\1"', c[2])
                            print("%s %s" % (codemapping[c[1]],par1))

                        elif (c[2] == '(i)'):
                            print("%s %s" % (codemapping[c[1]],'IND "I"'))

                    elif ((c[1] == 'HYP⁻¹')):
                        # _src: 3: ['g', 'HYP⁻¹', 'SIN']
                        par1 = op_trig.sub(r'A\1H', c[2])
                        print("%s" % (par1))

                    else:
                        print("## %s not matched3f3c" % c[1])

                elif ((c[1] == '→') or (c[1] == 'HYP')):
                    c23 = c[1]+c[2]
                    if c23 in codemapping:
                        print("%s" % (codemapping[c23]))
                    else:
                        if ((c[1] == 'HYP')):
                            # _src: 3: ['f', 'HYP', 'SIN']
                            par1 = op_trig.sub(r'\1H', c[2])
                            print("%s" % (par1))
                        else:
                            print("## %s not matched3f3d" % c[1])

                elif (c[1] == 'RESULT'):
                    # no result matrix in hp42s
                    print("%s" % ('STOP'))

                else:
                    print("_uma3: '%s': '%s'," % (c[1], c[1]))

            elif (ll == 3) and ((c[0] != 'f') or (c[0] != 'g')):
                if c[0] in codemapping:
                    #print("_map3: '%s': '%s'," % (c[0], codemapping[c[0]]))
                    operator = '#'
                    if c[1] in ops:
                        operator = ops[c[1]]

                    res1 = op_reg.match(c[0])
                    if res1:
                        if op_alpha.match(c[2]):
                            par1 = op_alpha.sub(r'"\1"', c[2])
                            if (c[1] == 'MATRIX'):
                                print("%s %s %s" % (codemapping[res1.group(1)],'MATRIX',par1))
                            else:
                                print("%s%s %s" % (codemapping[res1.group(1)],operator,par1))

                        elif op_num1.match(c[2]):
                            par1 = op_num1.sub(r'0\1', c[2])
                            print("%s%s %s" % (codemapping[res1.group(1)],operator,par1))

                        elif op_num2.match(c[2]):
                            par1 = op_num2.sub(r'1\1', c[2])
                            print("%s%s %s" % (codemapping[res1.group(1)],operator,par1))

                        elif (c[2] == '(i)'):
                            print("%s %s" % (codemapping[res1.group(1)],'IND "I"'))

                    else:
                        print("## %s not matched3" % c[0])

                else:
                    print("_uma3: '%s': '%s'," % (c[0], c[0]))

            elif (ll == 4) and ((c[0] == 'f') or (c[0] == 'g')):
                c123 = c[1]+c[2]+c[3]

                if c[0] in codemapping:
                    print("_map4: '%s%s%s': '%s%s%s'," % (c[1],c[2],c[3], c[1],c[2],c[3]))
                else:
                    if c123 in codemapping:
                        print("%s" % (codemapping[c123]))
                    else:
                        print("_uma4: '%s%s%s': '%s%s%s'," % (c[1],c[2],c[3], c[1],c[2],c[3]))

            else:
                print("_uma: '%s': '%s'," % (res.group(1), res.group(0)))




#---------------------------------------------------------------------------------------------------------

if len(sys.argv) != 2:
    print("usage: " + __file__ + " <file>")
    sys.exit(1)

# input
INFILE  = str(sys.argv[1])

txt = decode_file(INFILE,check_encoding(INFILE))

convert2hp42s(txt)

