# ImageTool

This is a command-line utility for binary image operations, including dividing, merging, extracting, and mixing.

## Usage
Run with Python 3

```bash
python3 JoshImageTool.py [options] SUBCOMMAND ...
```

## Commands

| Subcommand | Description                                                  |
|------------|--------------------------------------------------------------|
| `div`      | Divide the input image into two parts.                       |
| `mer`      | Merge two input images into one.                             |
| `ext`      | Extract contents from a given offset (or range) in an image. |
| `mix`      | Mix the first half of fileA with the second half of fileB.   |

## Example

```bash
# Divide 'input.bin' into two parts at the 1MB position.
python3 JoshImageTool.py div input.bin -l 1

# Divide 'input.bin' into two parts at the 100 byte position.
python3 JoshImageTool.py div input.bin -l 100 -b

# For more usage examples:
python3 JoshImageTool.py -u
```

## Testing

Run tests with pytest:

```bash
pytest test/
```
