import re
import os
import sys


NIQQUD_UNICODE = '[\u05b0-\u05b9\u05bc\u05bb\u05c2\u05c1]'
USAGE = f'usage: {os.path.basename(__file__)} path_to_txt_file output_file_path'


INPUT_FILE = 1
OUTPUT_FILE = 2
N_ARGS = 3


def deniqq(text):
    return re.sub(NIQQUD_UNICODE, '', text)


if __name__ == '__main__':
    if len(sys.argv) == N_ARGS:
        with open(sys.argv[INPUT_FILE], encoding='utf8') as input_fd:
            with open(sys.argv[OUTPUT_FILE], 'w', encoding='utf8') as output_fd:
                text = input_fd.read()
                output_fd.write(deniqq(text))
    else:
        print(USAGE)

