import glob
import json
import os
import threading
import paramiko


def download_and_delete(ip, username, password, path, name, delete):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, 22, username, password)
        sftp = ssh.open_sftp()
        print(f'Starting download for {name}')
        sftp.get(path+'invites.txt', f'./download/{name}.txt')
        print(f'Downloaded file from {name}')
        sftp.close()
        if delete:
            ssh.exec_command(f'true > {path}invites.txt')
            print(f'Deleted invites from {name}')
    except Exception as e:
        print(f'Error occured: {e}')
    finally:
        ssh.close()

def combine_invite_files():
    print('Combining invite files')
    files = glob.glob(os.path.join('./download', '*.txt'))

    unique_lines = set()
    for file in files:
        with open(file, 'r') as f:
            for line in f:
                unique_lines.add(line)

    with open('invites.txt', 'w') as f:
        f.writelines(unique_lines)
    print('Combined invite files and removed dupes. Saved to invites.txt.')

def remove_old_files():
    for filename in os.listdir('./download'):
        file_path = os.path.join('./download', filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    print('Removed all old invite files from the download folder')

if __name__ == '__main__':
    delete = False
    answered = False
    while not answered:
        i = input('Should the invites be deleted after downloading? (y/n)\nInput: ')
        if i == 'y':
            delete = True
            answered = True
        elif i == 'n':
            delete = False
            answered = True

    remove_old_files()

    with open('servers.json', 'r') as file:
        data = json.load(file)

    threads = []
    for name, data in data.items():
        t = threading.Thread(target=download_and_delete, args=(data['ip'], data['username'], data['password'], data['path_to_executable_folder'], name, delete))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

    print('Finished downloading')

    combine_invite_files()

    