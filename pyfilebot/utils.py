#!/usr/bin/env python
import os
import shutil
import re
from datetime import datetime

class Files:

    @staticmethod
    def remove_empty_folders(path, remove_root=True):
        if not os.path.isdir(path):
            return
        files = os.listdir(path)
        if len(files):
            for f in files:
                fullpath = os.path.join(path, f)
                if os.path.isdir(fullpath):
                    Files.remove_empty_folders(fullpath)
        files = os.listdir(path)
        if len(files) == 0 and remove_root:
            os.rmdir(path)

    @staticmethod
    def list(start_path, recur=True):
        extensions = ['avi', 'flv', 'm4v', 'mkv', 'mp4', 'mov', 'mpg', 'mpeg', 'wmv', 'srt']
        if os.path.isfile(start_path):
            yield start_path, os.path.basename(start_path)
        else:
            for dirpath, dirs, files in os.walk(start_path, topdown=True):
                for file in files:
                    absolute_path = os.path.abspath(os.path.join(dirpath, file))
                    ext = absolute_path.split('.')[-1]
                    if ext in extensions:
                        yield absolute_path, file
                if not recur:
                    break

    @staticmethod
    def process_rules(name, details):
        keys = re.findall(r"\{(\w+)\}", name)
        for key in keys:
            if key in list(details.__dict__.keys()):
                name = name.replace(f"{{{key}}}", str(getattr(details, key)))
            elif key == "season_0" or key == "episode_0":
                name = name.replace(f"{{{key}}}", str(getattr(details, key[:-2])).rjust(2, '0'))
            else:
                raise Exception(f"Unknown {key} variable")
        name = re.sub(r'[*?:"<>|]', "", name)
        return name

    @staticmethod
    def move(old_file, output_dir, new_name, force, dry_run):
        if output_dir:
            new_file = os.path.abspath(os.path.join(output_dir, new_name))
        else:
            new_file = os.path.abspath(os.path.join(os.path.dirname(old_file), new_name))
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        try:
            if old_file != new_file:
                if os.path.isfile(new_file):
                    if force:
                        os.remove(new_file)
                    else:
                        print(f"File skipped (already exists): {new_file}")
                        return
                if not dry_run:
                    shutil.move(old_file, new_file)
                    Files.write_history(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')};{old_file};{new_file}\n")
                print(f"{old_file}\n> {new_file}\n")

        except Exception as e:
            print(f"{e}")

    @staticmethod
    def write_history(content):
        with open('.history', 'a') as f:
            f.write(content)

    @staticmethod
    def read_history():
        with open('.history', 'r') as f:
            c = f.readlines()
            c.reverse()
        for i, line in enumerate(c):
            i_date, i_old_file, i_new_file = line.split(";")
            print(f"{i_date}:\n{i_old_file}\n> {i_new_file}")

    @staticmethod
    def rollback(old_path):
        with open('.history', 'r') as f:
            content = f.readlines()
        content.reverse()
        for i, line in enumerate(content):
            i_date, i_old_path, i_new_path = line.split(";")
            if i_new_path.strip() == old_path:
                os.makedirs(os.path.dirname(i_old_path), exist_ok=True)
                shutil.move(old_path, i_old_path)
                # Removing lines
                content.remove(line)
                with open(".history", "w") as f:
                    content.reverse()
                    f.writelines(content)
                print(f"{old_path}\n> {i_old_path}")
                break