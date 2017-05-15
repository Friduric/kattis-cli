# Kattis CLI for TDDD95

This is an updated version of
[kattis-cli](https://github.com/Kattis/kattis-cli) that uses
[beautiful soup](https://www.crummy.com/software/BeautifulSoup/) to
allow for listing accepted submissions. The tool will list all
problems that have been accepted and will do so in earliest first
fashion. Meaning you can look at the first accepted submission to a
problem and compare this against the deadline.

Also to be clear: I am not affiliated with Kattis in any way. I am a
student at Linköping University that is employed as an assistant in
the course TDDD95 and have decided to extend the kattis-cli, primarily
for use by TDDD95 students (but everyone else is welcome to!).

# Configuration file

Before running the submission client, you need to
[download a configuration file](https://liu.kattis.com/download/kattisrc). This
file includes a secret personal token that allows you to log in. It
should be placed in your home directory, or in the same directory as
`submit.py`, and be called `.kattisrc`.

# Installing dependencies

The program uses `requests` to do http requests and `beautifulsoup4`
with `lxml` to parse html. In order to install these either run `pip
install requests beautifulsoup4 lxml` or `pip install -r
requirements.txt`

# Running the client

The easiest way to use the client is if you have named your source
code to *problemid*.suffix, where suffix is something suitable for the
language (e.g., `.java` for Java, `.c` for C, `.cc` or `.cpp` for C++,
`.py` for Python, `.cs` for C#, `.go` for Go, and so on...).

Let's assume you're solving the problem
[Hello World!](https://open.kattis.com/problems/hello) (with problem
id `hello`) and that your java solution is in the file
`Hello.java`. Then you can simply run `submit.py Hello.java`, and the
client will make the correct guesses. You will always be prompted
before a submission is sent.

If you want to list your accepted submissions then run `python submit.py
--submissions`.

# More advanced options

The submit client can handle multiple files in a submission. For such
submissions, the filename and suffix of the first file listed on the
command line is the basis of the guesses. It is ok to list a file
multiple times, e.g., `submit.py Hello.java *.java` will work as
intended.

In case the client guesses wrong, you can correct it by specifying a
command line option. Running `submit.py -h` will list all options. The
options are:

* `-p <problem_id>`: overrides problem guess
* `-m <mainclass>`: overrides mainclass guess
* `-l <language>`: overrides language guess
* `-f`: forces submission (i.e., no prompt)
