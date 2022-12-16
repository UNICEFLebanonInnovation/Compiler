from rest_framework.response import Response
import requests
from requests.structures import CaseInsensitiveDict
import json
import copy
import logging
import io
import xlwt
import csv
from datetime import date
from django.http import HttpResponse, FileResponse
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Color
from datetime import datetime
logger = logging.getLogger(__name__)





