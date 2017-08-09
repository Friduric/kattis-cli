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

Also to be clear: I am not affiliated with Kattis in any way. I am a
student at Linköping University that is employed as an assistant in
the course TDDD95 and have decided to extend the kattis-cli, primarily
for use by TDDD95 students and teachers (but everyone else is welcome to!).

# Configuration file

Before running the downloader you will need a configuration file from
kattis. You can download yours
[here](https://liu.kattis.com/download/kattisrc) on how to download
this. The configuration file includes a secret personal token so make
sure to keep the file secret! Store it in your home directory as
`.kattisrc`

# Installing dependencies

The program uses a lot of different python libraries, these are
installed through pip by running

`pip install -r requirements.txt`

It would be wise to create a virtualenv for this tough, you can look
[here](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/)
to find out more about virtualenv

# Running

The program comes with some sample scripts that you can run that will
download your information, run the rules against your information or
if you are a teacher there is a script that will allow you to run the
rules against exported course data. All of these are located in the
`scripts` folder. Run them by positioning yourself in the root and
then run `./scripts/the_script_to_run.sh`
