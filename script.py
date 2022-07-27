import base64
from time import sleep
from datetime import datetime, timezone
from xmlrpc.client import Boolean
import requests
from requests.auth import HTTPBasicAuth
import gtin
import random
import string
import json

# Variables
api = "https://xx.pla.health/mappingEngine/demo.epi/demo.vault.xxx"
token = "xyxy" # for Authentication
headers = {"Content-Type": "application/json", "accept": "*/*", "token": token}

numberOfProducts = 1
numberOfBatches = 1 # per product
numberOfValidSerials = 10 # per batch
numberOfRecalledSerials = 3 # per batch

products = []
batches = []

expiryDate = "300101"

companyName = "TestCo"
receiverId = "ePI_TestReceiver"

leafletDirectory = "leaflet"
leafletFile = "export.xml"
extraFile = "figure_015_1452_0631_7048_4128.png"

successRequests = 0
errorRequests = 0

# Functions

def evaluateResponse(status_code):
    if status_code == 200:
        global successRequests
        successRequests += 1
    else:
        global errorRequests
        errorRequests += 1

# Create Products

for x in range(numberOfProducts):
    randomGtin = random.randint(1000000000000,9999999999999)
    gtinNumber = int(gtin.GTIN(raw=randomGtin))
    materialCode = randomGtin = random.randint(10000,99999)
    messageId = random.randint(1000000,999999999)
    currentTime = datetime.now().isoformat()
    name = "Sample Product " + ''.join(random.choices(string.ascii_uppercase, k=8))
    description = "Sample Description " + ''.join(random.choices(string.ascii_lowercase, k=16))

    payload = {
                "messageType": "Product",
                "messageTypeVersion": 1,
                "senderId": "PythonTestTool",
                "receiverId": receiverId,
                "messageId": str(messageId),
                "messageDateTime": currentTime,
                "product": {
                    "productCode": str(gtinNumber),
                    "internalMaterialCode": str(materialCode),
                    "inventedName": name,
                    "nameMedicinalProduct": description,
                    "strength": "2.5 mg",
                    "manufName": "",
                    "adverseEventReportingURL": "https://bayer.pla.health/borest/scan",
                    "acfProductCheckURL": "https://bayer.pla.health/borest/scan",
                    "flagEnableAdverseEventReporting": True,
                    "flagEnableACFProductCheck": True,
                    "flagDisplayEPI_BatchRecalled": True,
                    "flagDisplayEPI_SNRecalled": True,
                    "flagDisplayEPI_SNDecommissioned": True,
                    "flagDisplayEPI_SNUnknown": True,
                    "flagDisplayEPI_EXPIncorrect": True,
                    "flagDisplayEPI_BatchExpired": True,
                    "flagDisplayEPI_BatchNumberUnknown": True,
                    "healthcarePractitionerInfo": "SmPC",
                    "patientSpecificLeaflet": "Patient Information",
                    "markets": [
                    {
                        "marketId": "DE",
                        "nationalCode": "123456",
                        "mahName": companyName + " Germany",
                        "legalEntityName": companyName + " Germany AG"
                    }
                    ]
                }
            }
    
    products.append(gtinNumber)

    response = requests.put(api, headers=headers, data = json.dumps(payload))

    print(response)
    evaluateResponse(response.status_code)

print("Products: " + str(products))

# Create Batches

for x in products:
    for y in range(numberOfBatches):
        messageId = random.randint(1000000,999999999)
        currentTime = datetime.now().isoformat()
        randomBatch = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        validSerialNumbers = []
        recalledSerialNumbers = []
        for z in range(numberOfValidSerials):
            serial = random.randint(1000000000,9999999999)
            validSerialNumbers.append(str(serial))
        for z in range(numberOfRecalledSerials):
            serial = random.randint(1000000000,9999999999)
            recalledSerialNumbers.append(str(serial))

        batches.append([x, randomBatch])

        payload = {
                "messageType": "Batch",
                "messageTypeVersion": 1,
                "senderId": "PythonTestTool",
                "receiverId": receiverId,
                "messageId": str(messageId),
                "messageDateTime": currentTime,
                "batch": {
                    "productCode": str(x),
                    "batch": str(randomBatch),
                    "expiryDate": str(expiryDate),
                    "snValid": validSerialNumbers,
                    "snRecalled": recalledSerialNumbers,
                    "snDecom": [],
                    "recallMessage": "",
                    "batchMessage": "",
                    "packagingSiteName": "Leverkusen",
                    "flagEnableBatchRecallMessage": False,
                    "flagEnableSNVerification": True,
                    "flagEnableEXPVerification": True,
                    "flagEnableExpiredEXPCheck": True,
                    "flagEnableACFBatchCheck": False,
                    "acdcAuthFeatureSSI": "",
                    "acfBatchCheckURL": False,
                    "snValidReset": False,
                    "snRecalledReset": False,
                    "snDecomReset": False
                }
            }
        
        response = requests.put(api, headers=headers , data = json.dumps(payload))

        print(response)
        evaluateResponse(response.status_code)

print("Batches: " + str(batches))

# Create Leaflets

for x in products:

    shipmentId = rand = random.randint(10000000,99999999)

    leaflet = ""
    extra = ""
    with open(leafletDirectory + '/' + leafletFile, 'rb') as f:
        leaflet = base64.b64encode(f.read()).decode('utf-8')
    with open(leafletDirectory + '/' + extraFile, 'rb') as f:
        extra = base64.b64encode(f.read()).decode('utf-8')

    payload = {
        "messageTypeVersion": 1,
        "senderId": "PythonTestTool",
        "receiverId": receiverId,
        "messageId": str(messageId),
        "messageDateTime": currentTime,
        "productCode": str(x),
        "status": "new",
        "language": "de",
        "messageType": "leaflet",
        "xmlFileContent": str(leaflet),
        "otherFilesContent": [
            {
                "filename": extraFile,
                "fileContent": str(extra)
            }
        ]
    }
    
    response = requests.put(api, headers=headers , data = json.dumps(payload))
    print(response)
    evaluateResponse(response.status_code)

print("Script completed - Total Requests: " + str(successRequests + errorRequests) + " Successes: " + str(successRequests) + " Errors: " + str(errorRequests))