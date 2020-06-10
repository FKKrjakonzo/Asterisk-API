#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json
import ldap
import pydub
import io
import csv
from base64 import b64encode

NAME = 'XXXXXX'
PASSWORD = 'XXXXXX'
LOGIN = 'XXXXXX'
HEADERS = {'Content-type': 'application/json', 'charset': 'utf-8'}
AGENTS = {
    '10': 'XXXXXX',
    '20': 'XXXXXX',
    '30': 'XXXXXX',
    '40': 'XXXXXX',
    '50': 'XXXXXX',
    '60': 'XXXXXX',
    '70': 'XXXXXX',
    '80': 'XXXXXX',
    }
API_KEY = 'XXXXXX'
API_SITE = 'XXXXXX'
LDAP_SERVER = 'XXXXXX'
DATA_FILE = 'Data.csv'

"""Logging into API, returning token
"""
def login():
    r = requests.post(url=LOGIN + '/api/v1.1.0/login',
                      json={'username': NAME, 'password': PASSWORD,
                      'port': '8260'}, headers=HEADERS)
    connection = json.loads(r.text)
    if 'token' in connection:
        return connection['token']
    return False

"""Logging out of API, taking token as an input
"""
def logout(token):
    r = requests.post(url=LOGIN + '/api/v1.1.0/logout?token=' + token,
                      headers=HEADERS)
    if 'Success' in r.text:
        return True
    return False

"""Getting data URL, from API. 
"""
def get_string(token, times):
    if token:
        r = requests.post(url=LOGIN
                          + '/api/v1.1.0/cdr/get_random?token='
                          + token, json={'extid': 'all',
                          'starttime': times[0], 'endtime': times[1]},
                          headers=HEADERS)
        connection = json.loads(r.text)
        if 'random' in connection:
            return [token, connection['random']]
    return False

"""Getting sound file, from API. Returning "MP3" file. 
"""
def get_wav(token, name):
    if token:
        r = requests.post(url=LOGIN
                          + '/api/v1.1.0/recording/get_random?token='
                          + token, json={'recording': name},
                          headers=HEADERS)
        connection = json.loads(r.text)
        url = LOGIN \
            + '/api/v1.1.0/recording/download?recording={}&random={}&token={}'.format(name,
                connection['random'], token)
        myfile = requests.get(url)
        file_bytes = io.BytesIO(myfile.content)
        export = io.BytesIO()
        pydub.AudioSegment.from_file(file_bytes).export(export,
                format='mp3')

        return export
    return False

"""Downloading data, takes URL.
"""
def download(random, times):
    if random:
        url = LOGIN \
            + '/api/v1.1.0/cdr/download?extid=all&starttime={}&endtime={}&token={}&random={}'.format(times[0],
                times[1], random[0], random[1])
        myfile = requests.get(url)
        if 'errno' not in myfile.text:
            return myfile.text
    return False

"""Posting Data to OSTicket
"""
def post_ticket(data):
    header = {'X-API-Key': API_KEY}
    response = requests.post(API_SITE, data=json.dumps(data),
                             headers=header)
    return response.text

"""Saving data as logs into file.
"""
def append_list_as_row(line):
    with open(DATA_FILE, 'a') as f:
        f.write(line.replace(',', ';'))
        f.write('\n')

"""Decode string to UTF-8
"""
def decoder(name):
    return name[0].decode('utf-8')

"""Get data about callers from LDAP Query search
"""
def search(number):
    connect = ldap.initialize('ldap://' + LDAP_SERVER)
    connect.set_option(ldap.OPT_REFERRALS, 0)
    connect.simple_bind_s()
    result = connect.search_s('dc=okall', ldap.SCOPE_SUBTREE, 'mobile='
                              + number, ['givenName', 'sn', 'mail'])
    if not result:
        result = connect.search_s('dc=okall', ldap.SCOPE_SUBTREE,
                                  'mobile=' + '+420' + number,
                                  ['givenName', 'sn', 'mail'])
    if result:
        return (decoder(result[0][1]['sn']) + ' '
                + decoder(result[0][1]['givenName']),
                decoder(result[0][1]['mail']))
    return (0, 0)

"""Find if data was already passed to OSTicket
"""
def exists_in(number):
    with open(DATA_FILE, mode='r') as csvfile:
        reader = csv.reader(csvfile, skipinitialspace=True)
        for row in reader:
            if str(number) in row[0]:
                return True
    return False

"""Main data procession function, combines all together
"""
def data_process(data, token):
    ticket_data = data.split(',')
    if not exists_in(ticket_data[0]):
        (name, email) = search(ticket_data[2])

        if name == 0:
            name = 'Nezn\xc3\xa1m\xc3\xbd volaj\xc3\xadc\xc3\xad'
            email = 'nezami@kontakt.com'

        if '(' in ticket_data[3]:
            subject = 'Hovor s agentem - ' \
                + AGENTS[ticket_data[3].split('(')[1].replace(')', '')]
            ticketID = ticket_data[3].split('(')[1].replace(')', '')
        else:
            subject = 'Chyba subjektu'
            ticketID = ''

        (m, s) = divmod(ticket_data[5], 60)
        text = \
            '''Stav hovoru - {} 
Hovor p\xc5\x99ebehol - {} 
Hovor trval - {:02d}:{:02d}'''.format(ticket_data[8],
                ticket_data[1], m, s)
        test = {
            'alert': True,
            'autorespond': False,
            'source': 'API',
            'name': name,
            'email': email,
            'phone': ticket_data[2],
            'subject': subject,
            'topicId': '666-' + ticketID,
            'ip': '123.211.233.122',
            'message': text,
            }
        if ticket_data[11] != '':
            wav = get_wav(token, ticket_data[11])
            test['attachments'] = [{'recording.mp3': 'data:mpeg;base64,'

                                   + b64encode(wav.read()).decode('UTF-8'
                                   )}]
        i += ',' + post_ticket(test)
        append_list_as_row(i)
