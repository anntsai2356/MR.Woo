# mrwoo

mrwoo helps you find interested jobs posted on job search sites in Taiwan.
Now, view job opportunities using CLI on the terminal!

## Why use mrwoo

If you have the following conditions, recommend you try it. 

- Tired of searching back and forth on multiple job sites.
- The same vacancies keep popping up.
- Don't want to see job openings that I'm not interested in.

## supported job sites
 - [104](https://www.104.com.tw/jobs/main/)
 - [yourator](https://www.yourator.co/)
 - [cake resume](https://www.cakeresume.com/zh-TW)

## Requirements
 - Python >= 3.11.2
 - Git latest version

## Installation

### Step 1: Get the source code

```bash
git clone https://github.com/anntsai2356/mrwoo.git --depth=1
```

Tip: Use `--depth=1` to get the latest instead of the whole repository.

### Step 2: Set commend path

Find the bin folder path and append to the PATH variable in ZSH or BASH.

 - `export PATH="<bin_folder_path>:$PATH"`: export PATH setting
 - `<bin_folder_path>`: bin folder path

Note: Replace `<bin_folder_path>` to a true path.

Take ZSH for example:
```bash
# append to .zshrc
echo 'export PATH="<bin_folder_path>:$PATH"' >> ~/.zshrc

# restart .zshrc
source ~/.zshrc
```

### Step 3: Test

Check the command is work.
```bash
$ mrwoo -h
usage: mrwoo [-h] {fetch,browse} ...

mrwoo is a command line tool to browse jobs in the terminal.

positional arguments:
  {fetch,browse}
    fetch         fetch the job information from certain sites.
    browse        browse the job information from the specific file.

options:
  -h, --help      show this help message and exit
```

## Usage
```bash
# Job search by keyword "engineer" and export file in data folder.
# Default file name is jobs_YYYY-MM-DD.csv.
mrwoo fetch engineer

# View jobs one by one.
mrwoo browse data/jobs_YYYY-MM-DD.csv
```