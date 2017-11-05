
from student_registration.taskapp.celery import app


@app.task
def read_file():
    from openpyxl import load_workbook

    wb = load_workbook(filename='outreach_data.xlsx', read_only=True)
    ws = wb['big_data']

    for row in ws.rows:
        for cell in row:
            print(cell.value)
