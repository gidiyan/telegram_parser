import json
import os
import re
from datetime import datetime
from os.path import basename
from zipfile import ZipFile

from git import Repo, exc

import telegram_get_messages

# Getting today's messages
telegram_get_messages.main()

# variables for script
CommitMessage = 'Updating targets ' + datetime.now().strftime("%Y-%h-%d  %H:%M:%S")
HttpData = []
HttpsData = []
HttpsIpData = []
UdpData = []
TcpData80 = []
TcpData443 = []
TcpOtherData = []
repo = ''
ip_list = {}

# checking if repo is valid
try:
    repo = Repo('./')
except exc.NoSuchPathError as error:
    print('Not git repository: {}'.format(error))
    exit(1)


# print repo info
def print_repository(remote_repo):
    try:
        print('\nInfo On Repo')
        print('Repo Active Branch Is {}'.format(remote_repo.active_branch))
        for remote in remote_repo.remotes:
            print('Remote Named "{}" With URL "{}"'.format(remote, remote.url))
        print('Last Commit For Repo Is {}  at {}.'.format(str(repo.head.commit.hexsha),
                                                          str(repo.head.commit.committed_datetime)))
        print('Last Commit For Repo Is {}  at {}.'.format(str(repo.head.commit.message),
                                                          str(repo.head.commit.committed_datetime)))
    except AttributeError as e:
        print('An Exception Occurred In Getting Repository Info: {}'.format(e))


# push to repo
def git_push():
    try:
        repo.git.add(all=True)
        repo.index.commit(CommitMessage)
        origin = repo.remote(name='origin')
        origin.push()
        print('Successfully Pushed To Git')
    except:
        print('An Exception Cccurred: {}'.format(error))


# getting info and parsing it
def ip_parser(value):
    if re.search('/http|/https|/tcp|/udp', value):
        ip = value.split()[0]
        ports = re.search('\((.*?)\)', value).group(1)
        ip_list[ip] = ports


def ip_data_fulfill():
    for k, v in ip_list.items():
        if "80/http" in v:
            target = 'http://' + k + ':80'
            HttpData.append(target)
            target = 'tcp://' + k + ':80'
            TcpData80.append(target)
        if "443/https" in v:
            target = 'https://' + k + ':443'
            HttpsIpData.append(target)
            target = 'tcp://' + k + ':443'
            TcpData443.append(target)
        if v not in ("80/http", "443/https"):
            v = v.split(',')
            for item in v:
                if item.lstrip() != '80/http' and item.lstrip() != '443/https' and "/udp" not in item.lstrip():
                    target = 'tcp://' + k + ':' + item.lstrip().split('/')[0]
                    TcpOtherData.append(target)
        for item in v:
            check_udp = re.split('\W+',item)
            if 'udp' in check_udp:
                for item in v:
                    if '/tcp' not in item.lstrip() and "/udp" in item.lstrip():
                        target = 'udp://' + k + ':' + item.lstrip().split('/')[0]
                        UdpData.append(target)


def http_data_fulfil(value):
    if "https://" in value:
        HttpsData.append(value)
    elif "http://" in value:
        HttpData.append(value)


def get_data():
    file_in = open('channel_messages.json', 'r')
    json_data = json.load(file_in)
    for item in json_data:
        if 'message' in item.keys():
            message_text = item['message'].splitlines()
            for value in message_text:
                if "/http" in value or "/udp" in value or '/https' in value or '/tcp' in value:
                    ip_parser(value.lstrip().rstrip())
                if 'http://' in value or 'https://' in value:
                    if 'disbalancer' in value or 'chng.it' in value or 'change.org' in value or 'ddosukraine' in value:
                        continue
                    http_data_fulfil(value.lstrip().rstrip())
    ip_data_fulfill()
    file_in.close()


# creating files
def create_file(data, file_name, option):
    output_file = open(file_name, option)
    if type(data) is list:
        for item in data:
            output_file.write(item + '\n')
        output_file.close()
    if type(data) is str:
        output_file.write(data)


def join_data():
    str_data = '#targets updated ' + datetime.now().strftime("%d-%h-%Y \n\n")
    str_data += ' '.join(HttpData)
    str_data += ' --http-methods STRESS GET \n'
    str_data += ' '.join(HttpsData)
    str_data += ' --http-methods STRESS GET \n'
    str_data += ' '.join(HttpsIpData)
    str_data += ' --http-methods STRESS GET \n'
    return str_data


# creating backups
def FilesInDir(dirName, file_name, filter):
    with ZipFile(file_name, 'w') as zipObj:
        for folderName, subfolders, filenames in os.walk(dirName):
            for filename in filenames:
                if filter(filename):
                    file_path = os.path.join(folderName, filename)
                    zipObj.write(file_path, basename(file_path))


def create_backup():
    file_name = 'target_before_' + datetime.now().strftime("%m_%h_%Y_%H-%M-%S") + '.zip'
    print('*** Creating A Zip Archive Of Targets Lists Before update ***')
    FilesInDir('./', file_name, lambda name: '.lst' in name)


if __name__ == '__main__':
    get_data()
    print_repository(repo)
    print(
        f'\n\ntcp 80: {*TcpData80,}\n\ntcp 443: {*TcpData443,}\n\ntcp other: {*TcpOtherData,}\n\nhttp: {*HttpData,}\n\nhttps: {*HttpsData,}\n\nhttpsIp: {*HttpsIpData,}\n\n{*UdpData,}')
    create_backup()
    check_push = input('\npush to git? y/n\n')
    if check_push.lower() == "y":
        create_file(TcpData80, 'l4_tcp_80.lst', 'w')  # put desired name and data
        create_file(TcpData443, 'l4_tcp_443.lst', 'w')  # put desired name and data
        create_file(TcpOtherData, 'l4_tcp_other.lst', 'w')  # put desired name and data
        create_file(HttpData, 'l7_80.lst', 'w')  # put desired name and data
        create_file(HttpsData, 'l7_443.lst', 'w')  # put desired name and data
        create_file(HttpsIpData, 'l7_443.lst', 'a')  # put desired name and data
        create_file(UdpData, 'udp.lst', 'w')  # put desired name and data
        create_file(join_data(), 'targets.lst', 'w')  # put desired name
        create_file(TcpData80, 'l4_tcp_all.lst', 'w')  # put desired name and data
        create_file(TcpData443, 'l4_tcp_all.lst', 'a')  # put desired name and data
        create_file(TcpOtherData, 'l4_tcp_all.lst', 'a')  # put desired name and data
        create_file(HttpData, 'l7_all.lst', 'w')  # put desired name and data
        create_file(HttpsData, 'l7_all.lst', 'a')  # put desired name and data
        create_file(HttpsIpData, 'l7_all.lst', 'a')  # put desired name and data
        git_push()
    else:
        print("You Didn't Want to Push So Skipping")
