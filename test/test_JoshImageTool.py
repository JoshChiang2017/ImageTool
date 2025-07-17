import os
import sys
import tempfile
import shutil
import pytest

# Global file size for all test files
TEST_FILE_SIZE = 1024 * 1024 * 10  # 10 MB
TEST_SPLIT_SIZE = 256
TEST_SPLIT_SIZE_MB = 3
TEST_MIX_SIZE = 256
TEST_EXTRACT_BASE = 256
TEST_EXTRACT_SIZE = 128

# Set to True to keep directory of output files for debugging
DEBUG_KEEP_FILES = False

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import JoshImageTool

@pytest.fixture
def temp_bin_files():
    """
    Create a temp dir and multiple dummy binary files with random content.

    Returns:
        callable: A function taking `num_files` and returning:
            - temp_dir (str): path to the temp directory
            - file_list (List[str]): list of generated file paths
    """
    temp_dir = None

    def _create(num_files=1):
        nonlocal temp_dir
        if num_files < 1:
            raise ValueError("num_files must be >= 1")

        temp_dir = tempfile.mkdtemp() if not DEBUG_KEEP_FILES else os.getcwd()
        file_list = []

        for i in range(num_files):
            path = os.path.join(temp_dir, f"file_ori_{i+1}.bin") # Use 1-based index for file names
            data = os.urandom(TEST_FILE_SIZE)  # Use global file size
            with open(path, "wb") as f:
                f.write(data)
            file_list.append(path)

        return temp_dir, file_list

    yield _create

    if temp_dir and not DEBUG_KEEP_FILES:
        shutil.rmtree(temp_dir)

def test_image_divide(temp_bin_files):
    temp_dir, original_files = temp_bin_files(1)
    JoshImageTool.image_divide(original_files[0], str(TEST_SPLIT_SIZE), use_bytes=True, output_dir=temp_dir)

    files = [f for f in os.listdir(temp_dir) if "-1." in f or "-2." in f]
    assert len(files) == 2
    full_1 = os.path.join(temp_dir, [f for f in files if "-1." in f][0])
    full_2 = os.path.join(temp_dir, [f for f in files if "-2." in f][0])

    assert os.path.getsize(full_1) == TEST_SPLIT_SIZE
    assert os.path.getsize(full_2) == TEST_FILE_SIZE - TEST_SPLIT_SIZE

    with open(original_files[0], "rb") as f, open(full_1, "rb") as f1, open(full_2, "rb") as f2:
        original = f.read()
        part_1 = f1.read()
        part_2 = f2.read()

    assert part_1 == original[:TEST_SPLIT_SIZE]
    assert part_2 == original[TEST_SPLIT_SIZE:TEST_FILE_SIZE]

def test_image_divide_mb_mode(temp_bin_files):
    temp_dir, original_files = temp_bin_files(1)
    split_size_bytes = TEST_SPLIT_SIZE_MB * 1024 * 1024
    JoshImageTool.image_divide(original_files[0], str(TEST_SPLIT_SIZE_MB), use_bytes=False, output_dir=temp_dir)

    files = [f for f in os.listdir(temp_dir) if "-1." in f or "-2." in f]
    assert len(files) == 2
    full_1 = os.path.join(temp_dir, [f for f in files if "-1." in f][0])
    full_2 = os.path.join(temp_dir, [f for f in files if "-2." in f][0])

    assert os.path.getsize(full_1) == split_size_bytes
    assert os.path.getsize(full_2) == TEST_FILE_SIZE - split_size_bytes

    with open(original_files[0], "rb") as f, open(full_1, "rb") as f1, open(full_2, "rb") as f2:
        original = f.read()
        part_1 = f1.read()
        part_2 = f2.read()

    assert part_1 == original[:split_size_bytes]
    assert part_2 == original[split_size_bytes:TEST_FILE_SIZE]

def test_image_merge(temp_bin_files):
    temp_dir, original_files = temp_bin_files(2)
    JoshImageTool.image_merge(original_files[0], original_files[1], output_dir=temp_dir)

    files = [f for f in os.listdir(temp_dir) if "merge" in f]
    assert len(files) == 1
    merged_full = os.path.join(temp_dir, files[0])

    with open(original_files[0], "rb") as f1, open(original_files[1], "rb") as f2, open(merged_full, "rb") as f:
        part_1 = f1.read()
        part_2 = f2.read()
        output = f.read()
    
    assert output == part_1 + part_2

def test_image_mix(temp_bin_files):
    temp_dir, original_files = temp_bin_files(2)
    JoshImageTool.image_mix(original_files[0], original_files[1], str(TEST_MIX_SIZE), True, output_dir=temp_dir)

    files = [f for f in os.listdir(temp_dir) if "mix" in f]
    assert len(files) == 1
    mix_full = os.path.join(temp_dir, files[0])

    with open(original_files[0], "rb") as f1, open(original_files[1], "rb") as f2, open(mix_full, "rb") as f:
        part_1 = f1.read()
        part_2 = f2.read()
        output = f.read()

    
    expected = part_1[:TEST_MIX_SIZE] + part_2[TEST_MIX_SIZE:]
    print(expected[240:261].hex())
    print("--------------------")
    print(output[240:261].hex())
    assert output == expected

def test_image_extract(temp_bin_files):
    temp_dir, original_files = temp_bin_files(1)
    JoshImageTool.image_extract(original_files[0], str(TEST_EXTRACT_BASE), use_bytes=True, end_addr=None, extract_length=str(TEST_EXTRACT_SIZE), output_dir=temp_dir)

    files = [f for f in os.listdir(temp_dir) if "extract" in f]
    assert len(files) == 1
    extract_full = os.path.join(temp_dir, files[0])

    with open(original_files[0], "rb") as f, open(extract_full, "rb") as f1:
        original = f.read()
        extracted = f1.read()

    assert extracted == original[TEST_EXTRACT_BASE:TEST_EXTRACT_BASE+TEST_EXTRACT_SIZE]
