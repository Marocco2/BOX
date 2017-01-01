from box_lib import requests
import os

def box(sha=''):
    result = 0
    check_link = "https://api.github.com/repos/Marocco2/BOX/commits/shipping"
    headers = {'Accept': 'application/vnd.github.VERSION.sha'}
    r = requests.get(check_link, headers=headers)
    if sha == "":
        try:
            with open("sha.txt", 'r') as g:
                sha = g.read()
                g.close()
        except:
            update_status = "No SHA available"
            return update_status
    if r.text != sha:  # Check if server version and client version is the same
        download_link = "https://github.com/Marocco2/BOX/archive/shipping.zip"
        update_status = get_zipfile(download_link, dir_path)
        with open("apps\\python\\" + git_repo.split('/')[-1] + "\sha.txt", 'w') as j:
            j.write(r.text)
            j.close()
        return update_status
    else:
        update_status = "No new update"
        return update_status


def ac_app():
    result = 0

    return result