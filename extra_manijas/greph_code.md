# greph & egreph: Enhanced grep with header preservation

## What are `greph` and `egreph`?

These are Bash functions that behave just like `grep`, but with one key improvement:  
**they preserve the first line of input**, which is often a header (like from `ps`, `csv`, etc).

- `greph`: behaves like `grep`, but keeps the first line  
- `egreph`: behaves like `grep -E` (extended regex), and also keeps the first line

---

## Installation (Linux & WSL)

You can install these functions in any Bash-compatible shell.

### On Linux (Ubuntu, Debian, Fedora, Arch, etc.)

1. Open your terminal.
2. Edit your `.bashrc` file:
   nano ~/.bashrc
3. Add the following functions:

       # greph: grep wrapper that preserves the first line of input (e.g., headers)
       greph() {
           if [ "$#" -lt 1 ]; then
               echo "Usage: greph PATTERN [GREP_OPTIONS]" >&2
               return 1
           fi
           read -r header
           echo "$header"
           grep "$@"
       }

       # egreph: greph with extended regular expressions (equivalent to grep -E)
       egreph() {
           if [ "$#" -lt 1 ]; then
               echo "Usage: egreph PATTERN [GREP_OPTIONS]" >&2
               return 1
           fi
           read -r header
           echo "$header"
           grep -E "$@"
       }

4. Save and exit the editor.
5. Reload your shell:
   source ~/.bashrc

### On WSL (Windows Subsystem for Linux)

Same steps as Linux:

1. Open WSL (e.g., Ubuntu).
2. Edit `.bashrc`:
   nano ~/.bashrc
3. Paste the same function definitions shown above.
4. Save and reload:
   source ~/.bashrc

---

## Usage Examples

    ps aux | greph sshd
    # Shows all 'sshd' processes while keeping the column header

    ps aux | greph -v root
    # Excludes lines with 'root', but keeps the first line

    ps aux | egreph 'sshd|nginx'
    # Uses extended regex to match either 'sshd' or 'nginx'

    cat file.csv | greph "2025"
    # Greps for '2025' in a CSV file but preserves the header row

---

## How It Works

Ordinary `grep` filters all lines — including the first, which is often a header.  
These functions fix that by:

1. Reading the first line separately with `read -r header`
2. Immediately printing it back out using `echo "$header"`
3. Then piping the remaining input to `grep` or `grep -E`

This approach works in any pipeline and makes it easier to read filtered output when column names are important.

Both functions accept **all regular grep options**, such as:
- `-i` (ignore case)
- `-v` (invert match)
- `--color=auto`
- `-n` (line numbers)
- `-E` for extended regex (automatically used in `egreph`)

---

Happy grepping!
