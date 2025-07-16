#! python3
import sys
import time
import os
import argparse
import textwrap

def parse_length (length_string, length_as_binary):
    """
    Description:
        Convert a string of numbers to numbers. Strings that allow decimal or hexadecimal
        If it is hexadecimal input, it needs to start with '0x' or end with 'h'
        
        Will use length_as_binary to determine whether the unit of length is MB or BYTE
    """
        
    try:
        #
        # Convert the input length string to a number. And confirm whether the hexadecimal input.
        #
        length_string = length_string.strip().lower()
        if length_string.startswith('0x') or length_string.endswith('h'):
            length_string = length_string.replace('0x','')
            length_string = length_string.strip('h')
        
            length = int(length_string, 16)
            
        else:
            length = int(length_string)

        #
        # Define the units of the split length.
        # There are two mode to use, byte and megabyte.
        #
        if length_as_binary:
            print ("  <<<Operation in BYTE mode>>>")
        else :
            length = length * 1024 * 1024
            
        return length
    except ValueError:
    
        print("\n  ERROR!! Incorrect length input.")
        print("If it is hexadecimal input, it needs to start with 0x or end with h")
        return None

def file_check(*files):
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
            filelength = os.path.getsize(file)
            print(f'    Length of "{file}" is {filelength / 0x100000:.3f} MB ({filelength} bytes)')
    return all_exist

def image_extract (filename, range_start, length_as_binary, range_end, range_length):
    
    print ("=============================================")
    print ("<<< Extract image >>>")
    print ("File                : " + filename)
    print ("Start address       : " + range_start)
    print ("Length      (option): " + str (range_length))
    print ("End address (option): " + str (range_end))
    print ("=============================================")
    print ("  processing......")
    
    if not file_check(filename):
        return 
        
    start = parse_length (range_start, length_as_binary)
    if start == None:
        return 
    
    #
    # If there is range_length, it will be judged first.
    # If there is no range_length and range_end, it means to read all from start.
    #
    length = 0
    if range_length != None:
        length = parse_length (range_length, length_as_binary)
        if length == None:
            return 
    elif range_end != None:
        end = parse_length (range_end, length_as_binary)
        if end == None:
            return 
        length = end - start + 1
        
    if (start + length) > os.path.getsize(filename):
        print ("\n  ERROR!! Length or end address exceeds the file size.")
        return

    base = os.path.basename(filename)
    prefix, ext = os.path.splitext(base)
    ext = ext.lstrip('.')
    timestamp = time.strftime("%H_%M_%S", time.localtime())

    output_filename = f"{prefix}-EXTRACT-{timestamp}.{ext}"

    original_file = open(filename, 'rb')
    output_file = open(output_filename, 'wb')
    
    buffer = original_file.read(start)
    
    if length == 0:
        buffer = original_file.read()
    else:
        buffer = original_file.read(length)
    output_file.write (buffer)
    
    original_file.close()
    output_file.close()
    
    print ("\n  Extract finish!!!\n")
    file_check (output_filename)
    
def image_mix (filename1, filename2, length_of_first_half, length_as_binary):
    
    print ("=============================================")
    print ("<<< Mixing image >>>")
    print ("First  file   : " + filename1)
    print ("Second file   : " + filename2)
    print ("Mix    length : " + length_of_first_half)
    print ("=============================================")
    print ("  processing......")
    
    if not file_check(filename1, filename2):
        return 
        
    length = parse_length (length_of_first_half, length_as_binary)
    if length == None:
        return 
        
    output_filename = time.strftime("Mix_%H_%M_%S.bin", time.localtime())
    
    file1 = open(filename1, 'rb')
    file2 = open(filename2, 'rb')
    output_file = open(output_filename, 'wb')
    
    buffer = file1.read(length)
    output_file.write (buffer)
    
    buffer = file2.read(length) # read but not use to skip specific length
    buffer = file2.read()
    output_file.write (buffer)
    
    file1.close()
    file2.close()
    output_file.close()
    
    print ("\n  Mixing finish!!!\n")
    file_check (output_filename)

def image_merge (filename1, filename2):

    
    print ("=============================================")
    print ("<<< Merging image >>>")
    print ("First  file : " + filename1)
    print ("Second file : " + filename2)
    print ("=============================================")
    print ("  processing......")
    
    if not file_check(filename1, filename2):
        return 
        
    output_filename = time.strftime("Merge_%H_%M_%S.bin", time.localtime())
    
    file1 = open(filename1, 'rb')
    file2 = open(filename2, 'rb')
    output_file = open(output_filename, 'wb')
    
    buffer = file1.read()
    output_file.write (buffer)
    buffer = file2.read()
    output_file.write (buffer)
    
    file1.close()
    file2.close()
    output_file.close()
    
    print ("\n  Merging finish!!!\n")
    file_check (output_filename)

def image_divide (filename, length_of_first_half, length_as_binary):

    print ("=============================================")
    print ("<<< Dividing image >>>")
    print ("FileName     : " + filename)
    print ("Split length : " + length_of_first_half)
    print ("=============================================")
    print ("  processing......\n")
    
    if not file_check(filename):
        return 
        
    length = parse_length (length_of_first_half, length_as_binary)
    if length == None:
        return 
    
    base = os.path.basename(filename)
    prefix, ext = os.path.splitext(base)
    ext = ext.lstrip('.')
    timestamp = time.strftime("%H_%M_%S", time.localtime())

    filename1 = f"{prefix}-{timestamp}_A.{ext}"
    filename2 = f"{prefix}-{timestamp}_B.{ext}"

    original_file = open(filename, 'rb')
    file1 = open(filename1, 'wb')
    file2 = open(filename2, 'wb')
    
    buffer = original_file.read(length)
    file1.write (buffer)
    buffer = original_file.read()
    file2.write (buffer)
    
    original_file.close()
    file1.close()
    file2.close()
    
    print ("\n  Dividing finish!!!\n")
    file_check (filename1, filename2)

def build_parser():
    parser = argparse.ArgumentParser(
               description='Process binary images, including dividing, merging, extracting, and mixing.', 
               formatter_class=argparse.RawDescriptionHelpFormatter
               )
               
    parser.add_argument('-u', '--usage', help='Print some usage example.', action='store_true')
    sub_cmd = parser.add_subparsers(dest='sub_cmd', help='-------------------------', metavar='SUBCOMMAND')
    #sub_cmd.required=True
    
    #
    # subfunction - divide
    #
    description = textwrap.dedent('Divide the input image into two part.')
    parser_divide = sub_cmd.add_parser('div', formatter_class=argparse.RawDescriptionHelpFormatter ,description=description, help=description)
    parser_divide.add_argument('file', help='Image file to split.')
    parser_divide.add_argument('-l', dest='length', required=True, help='The length of the file to be split, which is the length of the first split file. (MB as default unit)')
    parser_divide.add_argument('-b', dest='length_as_binary', help='Using BYTE as the unit of length', action='store_true')
    
    #
    # subfunction - merge
    #
    description = textwrap.dedent('Merge two input images into complete one.')
    parser_merge = sub_cmd.add_parser('mer', formatter_class=argparse.RawDescriptionHelpFormatter ,description=description, help=description)
    parser_merge.add_argument('file1', help='Image file to split. (First half)')
    parser_merge.add_argument('file2', help='Image file to split. (Second half)')
    
    #
    # subfunction - extract
    #
    description = textwrap.dedent('''
        Extract the contents of an image specific address into a separate file.
          If there is range_length, it will be judged first.
          If there is no range_length and range_end, it means to read all from start.
        ''')
    parser_ext = sub_cmd.add_parser('ext', formatter_class=argparse.RawDescriptionHelpFormatter ,description=description, help=description)
    parser_ext.add_argument('file', help='Image file to extract.')
    parser_ext.add_argument('-s', dest='start', required=True, help='Start address of range. (MB as default unit)')
    parser_ext.add_argument('-e', dest='end', help='End address of range.')
    parser_ext.add_argument('-l', dest='length', help='Length of the range, has higher priority than -e (end).')
    parser_ext.add_argument('-b', dest='length_as_binary', help='Using BYTE as the unit', action='store_true')
    
    #
    # subfunction - mix
    #
    description = textwrap.dedent('''
        Mixing the first half of the fileA file with the second half of the fileB file.
          Both files should be the same length
        ''')
    parser_mix = sub_cmd.add_parser('mix', formatter_class=argparse.RawDescriptionHelpFormatter ,description=description, help=description)
    parser_mix.add_argument('file1', help='Image file to mix. (First half)')
    parser_mix.add_argument('file2', help='Image file to mix. (Second half)')
    parser_mix.add_argument('-l', dest='length', required=True, help='The length of the file to be split, which is the length of the first split file. (MB as default unit)')
    parser_mix.add_argument('-b', dest='length_as_binary', help='Using BYTE as the unit of length', action='store_true')
    
    usage=textwrap.dedent('''
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
    parser, usage= build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    if (args.usage == True):
        print (usage)
    elif (args.sub_cmd == 'div'):
        image_divide (args.file, args.length, args.length_as_binary)
        
    elif (args.sub_cmd == 'mer'):
        image_merge (args.file1, args.file2)
        
    elif (args.sub_cmd == 'mix'):
        image_mix (args.file1, args.file2, args.length, args.length_as_binary)
        
    elif (args.sub_cmd == 'ext'):
        image_extract (args.file, args.start, args.length_as_binary, args.end, args.length)
        
    else:
        print ('Subcommands are not implemented yet.')
    

if __name__ == "__main__":
    main()