# Kattis CLI for TDDD95

This program is designed to help teachers and students of TDDD95 with
grading. It is designed to help teachers get a good overview of how
students are performing but also help students see how well they are
performing, allowing them to easier attain their desired grade, as
well as giving them an overview of how they are doing.

The program mainly uses custom software to create rules for judging
student results, but it also uses the
[kattis-cli](https://github.com/Kattis/kattis-cli) for accessing
priviledged information (such as detailed submission
results). Kattis-cli is used to download the information as an HTML
page and then it is parsed using
[beautiful soup](https://www.crummy.com/software/BeautifulSoup/). The
data is then saved to an output file and can later be parsed by the
program

# Configuration file

Before running the downloader you will need a configuration file from
kattis. You can download yours [here](https://liu.kattis.com/download/kattisrc). 
The configuration file includes a secret personal token so make
sure to keep the file secret! Store it in your home directory as
`.kattisrc`.

# Running

In general this program requires that you have python3 and virtualenv
installed. If you have neither installed and you are on a ubuntu-like
system, then run `sudo apt-get install python3 && sudo pip
install -H virtualenv`.

### Teacher

Start by running the setup script: `./scripts/setup.sh`. Then download
course data from Kattis and put it inside `./data`. You can download any data, but we suggest that you download "All" instead
of "First accepted" or any other.

After this is done you can run `./scripts/teacher_main.sh` to see the
results of the students. This script looks for
`AAPS-AAPS18_export_all.json` inside the data directory, so if you get
a FileNotFound exception then change the script to use the correct file.
