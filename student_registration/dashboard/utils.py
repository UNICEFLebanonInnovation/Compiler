import subprocess


def export_full_data(params):

    command = params['report']
    subprocess.Popen(["python manage.py "+command, ], shell=True)
