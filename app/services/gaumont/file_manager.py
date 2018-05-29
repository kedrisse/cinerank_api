# -*- coding: utf-8 -*-
import os
import re
import time
import ssl
import urllib.request
import json
import sys
import io


def file_timestamp(name, file_name):
    return file_name[len(name) + 1::][:-5]


def load_json(content_url):
    ssl._create_default_https_context = ssl._create_unverified_context
    with urllib.request.urlopen(content_url) as url:
        return json.loads(url.read().decode())


class FileManager:

    @staticmethod
    def call(name, url, delay=604800):
        dir_path = os.path.dirname(os.path.realpath(__file__))+'/json_files'
        file_exists, timestamp, filename = FileManager.file_exists(name)
        if not file_exists or int(time.time()) > (int(timestamp)+delay): # si le fichier n'existe pas ou date de plus d'une semaine
            if file_exists and int(time.time()) > (int(timestamp)+delay):
                FileManager.delete_file(os.path.join(dir_path, filename))
            content = FileManager.create_file(url, name)
            return content
        else:
            return FileManager.get_file_content(filename)

    @staticmethod
    def file_exists(name):
        rootdir = os.path.dirname(os.path.realpath(__file__)) + '/json_files'
        regex = re.compile('(^' + name + '_[0-9]+\.json$)')

        for root, dirs, files in os.walk(rootdir):
            for file in files:
                if regex.match(file):
                    return True, file_timestamp(name, file), file
        return False, 0, None

    @staticmethod
    def delete_file(filename):
        if filename is None:
            return
        os.remove(filename)

    @staticmethod
    def create_file(url, name):
        ssl._create_default_https_context = ssl._create_unverified_context
        page = urllib.request.urlopen(url)
        content = page.read().decode('utf-8')

        dir_path = os.path.dirname(os.path.realpath(__file__))+'/json_files'
        filename = os.path.join(dir_path, name+"_"+str(int(time.time()))+".json")
        file = io.open(filename, "w", encoding='utf-8')
        file.write(content)
        file.close()

        return json.loads(content)

    @staticmethod
    def get_file_content(filename):
        dir_path = os.path.dirname(os.path.realpath(__file__))+'/json_files'
        fname = os.path.join(dir_path, filename)
        file = io.open(fname, 'r', encoding='utf-8')
        content = file.read()
        file.close()
        try:
            return json.loads(content)
        except json.decoder.JSONDecodeError:
            return None
