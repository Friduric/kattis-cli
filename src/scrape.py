import configparser
import collections
import pathlib
import util
import sys
import requests
import threading
import json

from urllib.parse import urlparse
from bs4 import BeautifulSoup


##########################################
# Error handlers                         #
##########################################

def default_crash_messages():
    return [
        'Something unexpected has happened and the program has crashed'
    ]


def crash_on(condition, function=default_crash_messages, *args):
    def print_and_crash():
        messages = function(*args)
        print('\n'.join(messages))
        sys.exit(1)
    util.crossroad(lambda: condition, print_and_crash, util.noop)



def config_error_messages(path):
    return [
        'Could not properly read the configuration file at "{}"'.format(path),
        'Suspect that it is badly formed'
    ]


def config_path_messages(custom_paths):
    return [
        'It looks like you did not fully configure your .kattisrc',
        'Make sure to go to the kattis help page and download it from there and',
        'then place it in your home folder as ".kattisrc"',
        'This search was done with default values and custom paths: {}'.format(custom_paths)
    ]


def failed_credentials_messages():
    return [
        'Your config file does not contain a password or a token, this is necessary',
        'in order to login and scrape the kattis pages. Are you sure you downloaded',
        'it correctly from the kattis webpage?'
    ]


def failed_website_messages():
    return [
        'Your kattisrc does not provide any hostname or loginurl.',
        'Are you sure you downloaded it correctly?'
    ]

def bad_credentials_messages():
    return [
        'Bad password and/or token provided as credentials.',
        'Please check your kattisrc'
    ]

def bad_credential_type_messages():
    return [
        'Programming error; Bad type for Credential'
    ]

def check_config_path_or_write_help_message(custom_paths=None):
    path = config_path(custom_paths)
    crash_on(not path, config_path_messages, custom_paths)


##########################################
# Config                                 #
##########################################


def config_path(custom_paths=None):
    custom_paths = custom_paths or []
    paths = [pathlib.Path(custom_path) for custom_path in custom_paths]
    paths += [
        pathlib.Path('/usr/local/etc/kattisrc'),
        pathlib.Path.home() / '.kattisrc',
        pathlib.Path.cwd() / '.kattisrc'
    ]
    path_exists = lambda p: p.exists()
    path = util.find(path_exists, paths)
    return None if not path else str(path)


def get_config(custom_paths=None):
    path = config_path(custom_paths)
    parser = configparser.ConfigParser()
    successful = parser.read(path)
    crash_on(not successful, config_error_messages, path)
    return parser


##########################################
# Login                                  #
##########################################


def get_headers():
    return {
        'User-Agent': 'TDDD95-scraper'
    }


Credentials = collections.namedtuple('Credentials', 'username type secret loginurl')


def make_credentials(username, password=None, token=None, loginurl=''):
    def has_password():
        return bool(password)
    def has_token():
        return bool(token)

    def return_with_password():
        return Credentials(username, 'password', password, loginurl)
    def return_with_token():
        return Credentials(username, 'token', token, loginurl)
    def crash():
        crash_on(True, bad_credentials_messages)

    return util.cond([
        (has_password, return_with_password),
        (has_token, return_with_token),
        (util.truthy, crash)
    ])()


def get_login_credentials(config):
    username = config.get('user', 'username')
    password = config.get('user', 'password', fallback=None)
    token = config.get('user', 'token', fallback=None)
    crash_on(not password and not token, failed_credentials_messages)

    hostname = config.get('kattis', 'hostname', fallback='')
    fallback_login = 'https://{}/{}'.format(hostname, 'login')
    loginurl = config.get('kattis', 'loginurl', fallback=fallback_login)
    fail_condition = not config.has_option('kattis', 'loginurl') and not hostname
    crash_on(fail_condition, failed_website_messages)
    return make_credentials(username, password, token, loginurl)


def get_login_parameters(credentials):
    login_args = {
        'user': credentials.username,
        'script': 'true',
    }
    def add_secret(key):
        login_args[key] = credentials.secret

    # Keep it as a map, if they change their interface then it doesn't match
    # ours. Harder to debug. Also if we screw up the type we will have a network
    # bug instead of a KeyError, big difference! (the BAD alternative would be to
    # just pass along the type, don't do that)
    choice = {
        'password': lambda: add_secret('password'),
        'token': lambda: add_secret('token')
    }
    def default_function():
        crash_on(True, bad_credential_type_messages)
    func = choice.get(credentials.type, default_function)
    func()
    return login_args


def login(config):
    credentials = get_login_credentials(config)
    loginurl = credentials.loginurl
    parameters = get_login_parameters(credentials)
    headers = get_headers()
    return requests.post(loginurl, data=parameters, headers=headers)


##########################################
# Scraping                               #
##########################################

def scrape_site(url, cookies, collector, destructor):
    headers = get_headers()
    response = requests.get(url, cookies=cookies, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find_all('table', class_='table-submissions')[0]
    rows = table.find_all('tbody')[0].find_all('tr')

    def has_no_entries():
        return not rows
    def process_row(row):
        data_items = row.find_all('td')
        # This is how the html is divided in the table cells.
        # Submission ID | Time | Name + link to problem | Status | runtime | language
        #      0        |   1  |          2             |   3    |   4     |   5
        problem_id = data_items[2].a['href'].split('/')[-1]
        problem_name = data_items[2].a.text
        status = data_items[3]['class']
        time = data_items[1].text
        return {
            'problem_id': problem_id,
            'problem_name': problem_name,
            'status': status,
            'time': time
        }
    def process_all_rows():
        data = util.map_now(process_row, rows)
        util.map_now(collector, data)

    return util.cond([
        (has_no_entries, destructor),
        (util.truthy, process_all_rows)
    ])()


def main():
    check_config_path_or_write_help_message()
    config = get_config()
    reply = login(config)
    def get_profile_page(idx):
        hostname = urlparse(config.get('kattis', 'loginurl')).netloc
        username = config.get('user', 'username')
        return 'https://{}/users/{}?page={}'.format(hostname, username, idx)

    # If someone has over 1000 pages then they surely will have no problem
    # finding out how this looks and rewriting this to work for them.
    one_thousand_pages = [get_profile_page(idx) for idx in range(1000)]
    allpages = collections.deque(one_thousand_pages)
    collected = collections.deque()
    page1 = allpages[0]
    def collector(info):
        collected.append(info)
        if len(collected) % 100 == 0:
            print('Collected at least {} entries'.format(100 * (len(collected) // 100)), file=sys.stderr)
    def destructor():
        return 'IShouldStopNow'

    def thread_main():
        for idx in range(100):
            try:
                page = allpages.popleft()
            except IndexError:
                return
            result = scrape_site(page, reply.cookies, collector, destructor)
            if result == 'IShouldStopNow':
                return
    threads = [threading.Thread(target=thread_main) for _ in range(10)]
    start_thread = lambda t: t.start()
    util.map_now(start_thread, threads)
    for thread in threads:
        thread.join()
    student = {
        'username': 'me',
        'name': 'Me',
        'email': '',
        'submissions': []
    }

    for submission in collected:
        judgement = 'Accepted' if 'accepted' in submission['status'] else 'Wrong Answer'
        item = {
            'time': submission['time'],
            'judgement': judgement,
            'problem': submission['problem_id']
        }
        student['submissions'].append(item)

    data = {
        "students": [
            student
        ],
        "sessions": []
    }
    print(json.dumps(data))


if __name__ == '__main__':
    main()
