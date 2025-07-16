#! python3
import sys
import time
import os
import argparse
import textwrap

def parse_length(length_string: str, use_bytes: bool):
    """
    Convert a numeric string (decimal or hexadecimal) to an integer length in bytes.

    Parameters:
        length_string (str): The input length string. Can be decimal (e.g. '10') or hex (e.g. '0x10', '10h').
        use_bytes (bool): If True, interpret value as bytes. If False, value is in megabytes (converted to bytes).

    Returns:
        int: The length in bytes, or None if input is invalid.
    """
        
    try:
        s = length_string.strip().lower()

        if s.startswith('0x') or s.endswith('h'):
            s = s.replace('0x','').strip('h')
            value = int(s, 16)
        else:
            value = int(s)

        if use_bytes:
            print ("  <<<Operation in BYTE mode>>>")
        else :
            if value > 10240:
                print("\nERROR: The specified length exceeds 10GB (10240MB) in MB mode.")
                print("Please input a smaller length.")
                return None
            value *= 1024 * 1024  # Convert MB to bytes
            
        return value

    except ValueError:
        print("\nERROR: Invalid length input.")
        print("Hint: Use '0x' prefix or 'h' suffix for hexadecimal.")
        return None

def check_files_exist(*files):
    """
    Check if all files exist. Accepts any number of file arguments.
    Prints file size if exists. Returns True only if all files exist.
    """
    all_exist = True
    for file in files:
        if not os.path.isfile(file):
            print(f'  ==> File "{file}" does not exist!!!')
            all_exist = False
        else:
            file_size = os.path.getsize(file)
            print(f'    Length of "{file}" is {file_size / 0x100000:.3f} MB ({file_size} bytes)')
    return all_exist

def generate_output_filenames(src_file, operation="op", output_dir=None, count=1):
    """
    Generate one or more output filenames based on the given operation type.

    Format: {output_dir}/{filename}-{timestamp}-{operation}-{number}.{ext}
    
    :param src_file: Path to the input file
    :param output_dir: Directory for output files; defaults to current working directory
    :param operation: Operation name string (e.g., 'div', 'merge', 'ext')
    :param count: Number of output files to generate
    :return: List of output file paths
    """
    filename, ext = os.path.splitext(os.path.basename(src_file))
    ext = ext.lstrip('.')
    timestamp = time.strftime("%H_%M_%S", time.localtime())

    if output_dir is None:
        output_dir = os.getcwd()

    return [
        os.path.join(output_dir, f"{filename}-{timestamp}-{operation}-{i+1}.{ext}")
        for i in range(count)
    ]

def image_extract(src_file, start_addr, use_bytes, end_addr, extract_length, output_dir=None):
    print("=============================================")
    print("<<< Extract image >>>")
    print("File                : " + src_file)
    print("Start address       : " + start_addr)
    print("Length      (option): " + str(extract_length))
    print("End address (option): " + str(end_addr))
    print("=============================================")
    print("  processing......")

    if not check_files_exist(src_file):
        return

    start = parse_length(start_addr, use_bytes)
    if start is None:
        return

    length = 0
    if extract_length is not None:
        length = parse_length(extract_length, use_bytes)
        if length is None:
            return
    elif end_addr is not None:
        end = parse_length(end_addr, use_bytes)
        if end is None:
            return
        length = end - start + 1

    if (start + length) > os.path.getsize(src_file):
        print("\n  ERROR!! Length or end address exceeds the file size.")
        return
    
    [output_file] = generate_output_filenames(src_file, operation="extract", output_dir=output_dir)

    with open(src_file, 'rb') as fin, open(output_file, 'wb') as fout:
        fin.read(start)
        if length == 0:
            data = fin.read()
        else:
            data = fin.read(length)
        fout.write(data)

    print("\n  Extract finish!!!\n")
    check_files_exist(output_file)
    
def image_mix(src_file_a, src_file_b, mix_length, use_bytes, output_dir=None):
    print("=============================================")
    print("<<< Mixing image >>>")
    print("First  file   : " + src_file_a)
    print("Second file   : " + src_file_b)
    print("Mix    length : " + mix_length)
    print("=============================================")
    print("  processing......")

    if not check_files_exist(src_file_a, src_file_b):
        return

    length = parse_length(mix_length, use_bytes)
    if length is None:
        return
        
    [output_file] = generate_output_filenames(src_file_a, operation="mix", output_dir=output_dir)

    with open(src_file_a, 'rb') as fa, open(src_file_b, 'rb') as fb, open(output_file, 'wb') as fout:
        fout.write(fa.read(length))
        fb.read(length)
        fout.write(fb.read())

    print("\n  Mixing finish!!!\n")
    check_files_exist(output_file)

def image_merge(src_file_a, src_file_b, output_dir=None):
    print("=============================================")
    print("<<< Merging image >>>")
    print("First  file : " + src_file_a)
    print("Second file : " + src_file_b)
    print("=============================================")
    print("  processing......")

    if not check_files_exist(src_file_a, src_file_b):
        return
        
    [output_file] = generate_output_filenames(src_file_a, operation="merge", output_dir=output_dir)

    with open(src_file_a, 'rb') as fa, open(src_file_b, 'rb') as fb, open(output_file, 'wb') as fout:
        fout.write(fa.read())
        fout.write(fb.read())

    print("\n  Merging finish!!!\n")
    check_files_exist(output_file)

def image_divide(src_file, split_length, use_bytes, output_dir=None):
    print("=============================================")
    print("<<< Dividing image >>>")
    print("File         : " + src_file)
    print("Split length : " + split_length)
    print("=============================================")
    print("  processing......\n")

    if not check_files_exist(src_file):
        return
        
    length = parse_length(split_length, use_bytes)
    if length is None:
        return
    
    [file_a, file_b] = generate_output_filenames(src_file, operation="div", output_dir=output_dir, count=2)

    with open(src_file, 'rb') as fin, open(file_a, 'wb') as fa, open(file_b, 'wb') as fb:
        fa.write(fin.read(length))
        fb.write(fin.read())
    
    print("\n  Dividing finish!!!\n")
    check_files_exist(file_a, file_b)

def build_parser():
    parser = argparse.ArgumentParser(
        description='Process binary images, including dividing, merging, extracting, and mixing.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-u', '--usage', help='Print some usage example.', action='store_true')
    sub_cmd = parser.add_subparsers(dest='sub_cmd', help='-------------------------', metavar='SUBCOMMAND')
    #sub_cmd.required=True

    # divide
    desc = textwrap.dedent('Divide the input image into two parts.')
    parser_div = sub_cmd.add_parser('div', formatter_class=argparse.RawDescriptionHelpFormatter, description=desc, help=desc)
    parser_div.add_argument('file', help='Image file to split.')
    parser_div.add_argument('-l', dest='length', required=True, help='The length of the first split file. (MB as default unit)')
    parser_div.add_argument('-b', dest='use_bytes', help='Use BYTE as the unit of length', action='store_true')

    # merge
    desc = textwrap.dedent('Merge two input images into one.')
    parser_mer = sub_cmd.add_parser('mer', formatter_class=argparse.RawDescriptionHelpFormatter, description=desc, help=desc)
    parser_mer.add_argument('file1', help='First image file.')
    parser_mer.add_argument('file2', help='Second image file.')

    # extract
    desc = textwrap.dedent('''
        Extract the contents of an image from a specific address into a separate file.
        If length is specified, it takes priority.
        If neither length nor end is specified, reads all from start.
    ''')
    parser_ext = sub_cmd.add_parser('ext', formatter_class=argparse.RawDescriptionHelpFormatter, description=desc, help=desc)
    parser_ext.add_argument('file', help='Image file to extract.')
    parser_ext.add_argument('-s', dest='start', required=True, help='Start address of range. (MB as default unit)')
    parser_ext.add_argument('-e', dest='end', help='End address of range.')
    parser_ext.add_argument('-l', dest='length', help='Length of the range, has higher priority than -e (end).')
    parser_ext.add_argument('-b', dest='use_bytes', help='Use BYTE as the unit', action='store_true')

    # mix
    desc = textwrap.dedent('''
        Mix the first half of fileA with the second half of fileB.
        Both files should be the same length.
    ''')
    parser_mix = sub_cmd.add_parser('mix', formatter_class=argparse.RawDescriptionHelpFormatter, description=desc, help=desc)
    parser_mix.add_argument('file1', help='First image file. (First half)')
    parser_mix.add_argument('file2', help='Second image file. (Second half)')
    parser_mix.add_argument('-l', dest='length', required=True, help='Length of the first split file. (MB as default unit)')
    parser_mix.add_argument('-b', dest='use_bytes', help='Use BYTE as the unit of length', action='store_true')

    usage = textwrap.dedent('''
        Usage example:
          Suppose there are two 64MB full images fileX and fileY.
          
          Case: Divide fileX into two images of 2MB and 62MB
             JoshImageTool.py div fileX -l 2
             
          Case: Divide fileX into two images of 1024 byte and others part with byte
             JoshImageTool.py div fileX -l 1024 -b
             JoshImageTool.py div fileX -l 0x400 -b
             
          Case: Merge fileX and fileY into a 128MB image
             JoshImageTool.py mer fileX fileY
             
          Case: Mix the first 48MB of fileX and the last 16MB of fileY into a 64MB image
             JoshImageTool.py mix fileX fileY -l 48
             
          Case: Extract the content from 10MB to 12MB in fileX into a separate Image
             JoshImageTool.py ext fileX -s 10 -l 2
             JoshImageTool.py ext fileX -s 0xA00000 -l 0x200000 -b
             JoshImageTool.py ext fileX -s 0xA00000 -e 0x1fffff -b
    ''')
    return parser, usage

def main():
    parser, usage = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    if args.usage:
        print(usage)
    elif args.sub_cmd == 'div':
        image_divide (args.file, args.length, args.use_bytes)
    elif args.sub_cmd == 'mer':
        image_merge (args.file1, args.file2)
    elif args.sub_cmd == 'mix':
        image_mix (args.file1, args.file2, args.length, args.use_bytes)
    elif args.sub_cmd == 'ext':
        image_extract (args.file, args.start, args.use_bytes, args.end, args.length)
    else:
        print('Subcommands are not implemented yet.')

if __name__ == "__main__":
    main()