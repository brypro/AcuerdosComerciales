from fastapi import FastAPI
import json
import urllib3
import requests
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

global g_mntacum, g_mntplan

@app.get("/")
def index():
    return {"Hello": "World"}

@app.get("/AcuerdosComerciales")
def get_data():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    API_ENDPOINT = "https://23.88.83.123:50047/b1s/v1/Login"

    data = {
        'CompanyDB': 'ZZ_VINOTECA_11122024',
        'UserName': 'integradorDW',
        'Password': 'X.Lv3Ee.2B'
    }

    r = requests.post(url=API_ENDPOINT, json=data, verify=False)

    b1session_cookie = r.cookies.get('B1SESSION')
    b1session_ROUTEID = r.cookies.get('ROUTEID')

    class Aglobal(BaseModel):
        nroacuerdotulo: str
        fecini: str
        fecfin: str
        mntinversion: int
        importeacum: float
        importeplan: float

    url = "https://23.88.83.123:50047/b1s/v1/BlanketAgreements?$select=DocNum,StartDate,EndDate,U_Monto_Inversion,BlanketAgreements_ItemsLines&$filter=BPCode eq 'C78016900-1'"
    headers = {
        "Cookie": "B1SESSION=" + b1session_cookie + "; ROUTEID=" + b1session_ROUTEID,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        orders_data = response.json()

        value_list = orders_data.get("value", [])
        results = []

        for agreement in value_list:
            x_docnum = agreement.get("DocNum")
            x_startdate = agreement.get("StartDate")
            x_enddate = agreement.get("EndDate")
            x_monto_inversion = agreement.get("U_Monto_Inversion")

            items_lines = agreement.get("BlanketAgreements_ItemsLines", [])

            for line in items_lines:
                x_mntacum = float(line.get('CumulativeAmountLC', 0.0))
                x_mntplan = float(line.get('PlannedAmountLC', 0.0))
                g_mntacum = x_mntacum
                g_mntplan = x_mntplan

                fecha_original = datetime.strptime(x_startdate, "%Y-%m-%dT%H:%M:%SZ")
                fecha_inicio = fecha_original.strftime("%Y%m%d")

                fecha_original = datetime.strptime(x_enddate, "%Y-%m-%dT%H:%M:%SZ")
                fecha_fin = fecha_original.strftime("%Y%m%d")

                results.append({
                    'DocNum': x_docnum,
                    'FechaIni': fecha_inicio,
                    'FechaFin': fecha_fin,
                    'MontoInversion': x_monto_inversion,
                    'MontoAcum': g_mntacum,
                    'MontoPlan': g_mntplan,
                   
                })

        return  results
    else:
        return {"error": response.status_code, "message": response.text}