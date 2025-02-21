import json
import re
import requests
import time
import datetime


def get_apps_by_country(countryCode, year): 
    url = "https://ped.uspto.gov/api/queries"

    if year == datetime.datetime.now().year:
        end_time = time.strftime("%Y-%m-%d")
        time_range = "appStatusDate:["+ year + "-01-01T00:00:00Z TO " + end_time + "T23:59:59Z]"
    else:
        time_range = "appStatusDate:["+ year + "-01-01T00:00:00Z TO " + year + "-12-31T23:59:59Z]"

    search_query_txt = "inventors:[{country:("+ countryCode + ")}]"

    payload = json.dumps({
        "df": "patentTitle",
        "facet": "true",
        "fl": "*",
        "fq": [time_range],
        "mm": "0%",
        "qf": "appEarlyPubNumber applId appLocation appType appStatus_txt appConfrNumber appCustNumber appGrpArtNumber appCls appSubCls appEntityStatus_txt patentNumber patentTitle inventorName firstNamedApplicant appExamName appExamPrefrdName appAttrDockNumber appPCTNumber appIntlPubNumber wipoEarlyPubNumber pctAppType firstInventorFile appClsSubCls rankAndInventorsList",
        "searchText": search_query_txt,
        "sort": "applId asc",
        "start": "0"
    })

    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'Content-Type': 'application/json',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'host': 'ped.uspto.gov'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def get_apps_by_case_status(status, year):
    url = "https://ped.uspto.gov/api/queries"

    if year == datetime.datetime.now().year:
        end_time = time.strftime("%Y-%m-%d")
        time_range = "appStatusDate:["+ year + "-01-01T00:00:00Z TO " + end_time + "T23:59:59Z]"
    else:
        time_range = "appStatusDate:["+ year + "-01-01T00:00:00Z TO " + year + "-12-31T23:59:59Z]"

    status_query_txt = "appStatus_txt:" + status
    payload = json.dumps({
        "df": "patentTitle",
        "facet": "true",
        "fl": "*",
        "fq": [time_range],
        "mm": "0%",
        "qf": "appEarlyPubNumber applId appLocation appType appStatus_txt appConfrNumber appCustNumber appGrpArtNumber appCls appSubCls appEntityStatus_txt patentNumber patentTitle inventorName firstNamedApplicant appExamName appExamPrefrdName appAttrDockNumber appPCTNumber appIntlPubNumber wipoEarlyPubNumber pctAppType firstInventorFile appClsSubCls rankAndInventorsList",
        "searchText": status_query_txt,
        "sort": "applId asc",
        "start": "0"
    })

    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'Content-Type': 'application/json',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'host': 'ped.uspto.gov'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def get_app_doc_list(applId):
    try:
        response = requests.get(f'https://ped.uspto.gov/api/queries/cms/public/{applId}')

        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None


def get_app_docs(applId):
    list = get_app_doc_list(applId)
    docs = []

    for doc in list:
        if re.search('Power of Attorney', doc['documentDescription']):
            pass

        url = 'https://ped.uspto.gov/api/queries/cms/pdfDocument/' + doc['applicationNumberText'] + '/' + doc['documentIdentifier']
        r = requests.get(url, stream=True)
        file_path = '../pdfs/' + doc["applicationNumberText"] + '-' + doc["documentIdentifier"] + '.pdf'
        # docs.extend(PyPDFLoader(file_path).load())
        
        with open(file_path, 'wb') as fd:
            for chunk in r.iter_content(r.content):
                fd.write(chunk)
    
        # rate limit 1 doc/min
        time.sleep(300)

    return docs

# import requests
# import json

# url = "https://patentcenter.uspto.gov/retrieval/public/v1/documents"

# payload = json.dumps({
#   "fileTitleText": "Multi-file-download",
#   "documentInformationBag": [
#     {
#       "bookmarkTitleText": "84561_16948574_01-23-2024_eGrant day-of Notification",
#       "documentIdentifier": "LRPWRG1CXBLUEX2",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "01-23-2024",
#       "documentCode": "EGRANT.NTF",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_01-03-2024_Issue Notification",
#       "documentIdentifier": "LQY6KEP4GREENX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "01-03-2024",
#       "documentCode": "ISSUE.NTF",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-12-2023_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LQ2QQX88REENX11",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-12-2023",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-12-2023_Electronic Fee Payment",
#       "documentIdentifier": "LQ2QQX89REENX11",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-12-2023",
#       "documentCode": "N417.PYMT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-12-2023_Issue Fee Payment (PTO-85B)",
#       "documentIdentifier": "LQ2QQX8AREENX11",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-12-2023",
#       "documentCode": "IFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-12-2023_Miscellaneous Incoming Letter",
#       "documentIdentifier": "LQ2QQX8BREENX11",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-12-2023",
#       "documentCode": "LET.",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Notice of Allowance and Fees Due (PTOL-85)",
#       "documentIdentifier": "LMQI1X3EXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "NOA",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_List of references cited by examiner",
#       "documentIdentifier": "LMQI1X3MXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "892",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Issue Information including classification, examiner, name, claim, renumbering, etc.",
#       "documentIdentifier": "LMQI1X3VXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "IIFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Search information including classification, databases and other search related notes",
#       "documentIdentifier": "LMQI1X44XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "SRFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Index of Claims",
#       "documentIdentifier": "LMQI1X4CXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "FWCLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Bibliographic Data Sheet",
#       "documentIdentifier": "LMQI1X4LXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "BIB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LMQI1X4UXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LMQI1X53XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LMQI1X5CXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_List of References cited by applicant and considered by examiner",
#       "documentIdentifier": "LMQI1X5LXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "1449",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_08-17-2023_Information Disclosure Statement (IDS) Form (SB08)",
#       "documentIdentifier": "LLFUGBDFXBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "08-17-2023",
#       "documentCode": "IDS",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_08-17-2023_Fee Worksheet (SB06)",
#       "documentIdentifier": "LLFUGBE2XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "08-17-2023",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_08-17-2023_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LLFUGBE9XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "08-17-2023",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_08-17-2023_Request for Continued Examination (RCE)",
#       "documentIdentifier": "LLFUG9PYXBLUEX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "08-17-2023",
#       "documentCode": "RCEX",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Notice of Allowance and Fees Due (PTOL-85)",
#       "documentIdentifier": "LIJ4N4QXXBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "NOA",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Examiner Interview Summary Record (PTOL - 413)",
#       "documentIdentifier": "LIJ4N4QYXBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "EXIN",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_List of references cited by examiner",
#       "documentIdentifier": "LIJ4N4QZXBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "892",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Issue Information including classification, examiner, name, claim, renumbering, etc.",
#       "documentIdentifier": "LIJ4N4R0XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "IIFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Search information including classification, databases and other search related notes",
#       "documentIdentifier": "LIJ4N4R1XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "SRFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Index of Claims",
#       "documentIdentifier": "LIJ4N4R2XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "FWCLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LIJ4N4R3XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Amendment After Final or under 37CFR 1.312, initialed by the examiner.",
#       "documentIdentifier": "LIJ4N4R4XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "ANE.I",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LIJ4N4R5XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Bibliographic Data Sheet",
#       "documentIdentifier": "LIJ4N4R7XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "BIB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Response After Final Action",
#       "documentIdentifier": "LH18TDM2XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "A.NE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Claims",
#       "documentIdentifier": "LH18TDM3XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "CLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Applicant Arguments/Remarks Made in an Amendment",
#       "documentIdentifier": "LH18TDM4XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "REM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LH18TDM6XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Fee Worksheet (SB06)",
#       "documentIdentifier": "LH6PHPY6XBLUEX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Final Rejection",
#       "documentIdentifier": "LEN8UO5OGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "CTFR",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_List of references cited by examiner",
#       "documentIdentifier": "LEN8UO5PGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "892",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Search information including classification, databases and other search related notes",
#       "documentIdentifier": "LEN8UO5QGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "SRFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Index of Claims",
#       "documentIdentifier": "LEN8UO5RGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "FWCLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Bibliographic Data Sheet",
#       "documentIdentifier": "LEN8UO5SGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "BIB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LEN8UO5TGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_List of References cited by applicant and considered by examiner",
#       "documentIdentifier": "LEN8UO5UGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "1449",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LEN8UO5WGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LEN8UO5XGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Information Disclosure Statement (IDS) Form (SB08)",
#       "documentIdentifier": "LBH6XQFFXBLUEX2",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "IDS",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Fee Worksheet (SB06)",
#       "documentIdentifier": "LBH6XQFHXBLUEX2",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LBH6XQFIXBLUEX2",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Amendment/Request for Reconsideration-After Non-Final Rejection",
#       "documentIdentifier": "LBH6MZOHXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "A...",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Claims",
#       "documentIdentifier": "LBH6MZOJXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "CLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Applicant Arguments/Remarks Made in an Amendment",
#       "documentIdentifier": "LBH6MZOKXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "REM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LBH6MZOLXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Fee Worksheet (SB06)",
#       "documentIdentifier": "LBPRSQA5XBLUEX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Non-Final Rejection",
#       "documentIdentifier": "L7S01XN8XBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "CTNF",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_List of references cited by examiner",
#       "documentIdentifier": "L7S01XN9XBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "892",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Index of Claims",
#       "documentIdentifier": "L7S01XNAXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "FWCLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Search information including classification, databases and other search related notes",
#       "documentIdentifier": "L7S01XNBXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "SRFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_List of References cited by applicant and considered by examiner",
#       "documentIdentifier": "L7S01XNCXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "1449",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Examiner's search strategy and results",
#       "documentIdentifier": "L7S01XNDXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Bibliographic Data Sheet",
#       "documentIdentifier": "L7S01XNEXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "BIB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Examiner's search strategy and results",
#       "documentIdentifier": "L7S01XNGXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-15-2021_Information Disclosure Statement (IDS) Form (SB08)",
#       "documentIdentifier": "KPYPADO1DFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-15-2021",
#       "documentCode": "IDS",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-15-2021_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "KPYPADO5DFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-15-2021",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-25-2021_Notice of Publication",
#       "documentIdentifier": "KMP4JFS0DFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-25-2021",
#       "documentCode": "NTC.PUB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-30-2020_Fee Worksheet (SB06)",
#       "documentIdentifier": "KFO0PJ8TLDFLYX9",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-30-2020",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-30-2020_Filing Receipt",
#       "documentIdentifier": "KFO0PIJFDFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-30-2020",
#       "documentCode": "APP.FILE.REC",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Oath or Declaration filed",
#       "documentIdentifier": "KFG167MHRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "OATH",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Drawings-only black and white line drawings",
#       "documentIdentifier": "KFG167MIRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "DRW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Application Data Sheet",
#       "documentIdentifier": "KFG167MJRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "ADS",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "KFG167MKRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Electronic Fee Payment",
#       "documentIdentifier": "KFG167MLRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "N417.PYMT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Specification",
#       "documentIdentifier": "KFI34T7ELDFLYX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "SPEC",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Claims",
#       "documentIdentifier": "KFI34T7FLDFLYX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "CLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Abstract",
#       "documentIdentifier": "KFI34T7GLDFLYX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "ABST",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Placeholder sheet indicating presence of supplemental content in Supplemental Complex Repository for Examiners(SCORE)",
#       "documentIdentifier": "KFYBBJL5DFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "SCORE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     }
#   ],
#   "downloadType": "pdfzip",
#   "rid": "4399465d-4ad4-40f4-8fe0-27d8b6948e01"
# })
# headers = {
#   'X-INSTANA-L': '1,correlationType=web;correlationId=1292d7bdd85a7d19',
#   'X-INSTANA-S': '1292d7bdd85a7d19',
#   'sec-ch-ua-platform': '"Windows"',
#   'X-INSTANA-T': '1292d7bdd85a7d19',
#   'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
#   'sec-ch-ua-mobile': '?0',
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
#   'Accept': 'application/json, text/plain, */*',
#   'DNT': '1',
#   'Content-Type': 'application/json',
#   'Sec-Fetch-Site': 'same-origin',
#   'Sec-Fetch-Mode': 'cors',
#   'Sec-Fetch-Dest': 'empty',
#   'host': 'patentcenter.uspto.gov'
# }

# response = requests.request("POST", url, headers=headers, data=payload)

# print(response.text)

# import requests
# import json

# url = "https://patentcenter.uspto.gov/retrieval/public/v1/documents"

# payload = json.dumps({
#   "fileTitleText": "KVWVO732LDFLYX2",
#   "documentInformationBag": [
#     {
#       "bookmarkTitleText": "84561_16948574_01-23-2024_eGrant day-of Notification",
#       "documentIdentifier": "LRPWRG1CXBLUEX2",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "01-23-2024",
#       "documentCode": "EGRANT.NTF",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_01-03-2024_Issue Notification",
#       "documentIdentifier": "LQY6KEP4GREENX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "01-03-2024",
#       "documentCode": "ISSUE.NTF",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-12-2023_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LQ2QQX88REENX11",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-12-2023",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-12-2023_Electronic Fee Payment",
#       "documentIdentifier": "LQ2QQX89REENX11",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-12-2023",
#       "documentCode": "N417.PYMT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-12-2023_Issue Fee Payment (PTO-85B)",
#       "documentIdentifier": "LQ2QQX8AREENX11",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-12-2023",
#       "documentCode": "IFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-12-2023_Miscellaneous Incoming Letter",
#       "documentIdentifier": "LQ2QQX8BREENX11",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-12-2023",
#       "documentCode": "LET.",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Notice of Allowance and Fees Due (PTOL-85)",
#       "documentIdentifier": "LMQI1X3EXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "NOA",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_List of references cited by examiner",
#       "documentIdentifier": "LMQI1X3MXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "892",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Issue Information including classification, examiner, name, claim, renumbering, etc.",
#       "documentIdentifier": "LMQI1X3VXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "IIFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Search information including classification, databases and other search related notes",
#       "documentIdentifier": "LMQI1X44XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "SRFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Index of Claims",
#       "documentIdentifier": "LMQI1X4CXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "FWCLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Bibliographic Data Sheet",
#       "documentIdentifier": "LMQI1X4LXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "BIB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LMQI1X4UXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LMQI1X53XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LMQI1X5CXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-21-2023_List of References cited by applicant and considered by examiner",
#       "documentIdentifier": "LMQI1X5LXBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-21-2023",
#       "documentCode": "1449",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_08-17-2023_Information Disclosure Statement (IDS) Form (SB08)",
#       "documentIdentifier": "LLFUGBDFXBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "08-17-2023",
#       "documentCode": "IDS",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_08-17-2023_Fee Worksheet (SB06)",
#       "documentIdentifier": "LLFUGBE2XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "08-17-2023",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_08-17-2023_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LLFUGBE9XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "08-17-2023",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_08-17-2023_Request for Continued Examination (RCE)",
#       "documentIdentifier": "LLFUG9PYXBLUEX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "08-17-2023",
#       "documentCode": "RCEX",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Notice of Allowance and Fees Due (PTOL-85)",
#       "documentIdentifier": "LIJ4N4QXXBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "NOA",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Examiner Interview Summary Record (PTOL - 413)",
#       "documentIdentifier": "LIJ4N4QYXBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "EXIN",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_List of references cited by examiner",
#       "documentIdentifier": "LIJ4N4QZXBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "892",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Issue Information including classification, examiner, name, claim, renumbering, etc.",
#       "documentIdentifier": "LIJ4N4R0XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "IIFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Search information including classification, databases and other search related notes",
#       "documentIdentifier": "LIJ4N4R1XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "SRFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Index of Claims",
#       "documentIdentifier": "LIJ4N4R2XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "FWCLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LIJ4N4R3XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Amendment After Final or under 37CFR 1.312, initialed by the examiner.",
#       "documentIdentifier": "LIJ4N4R4XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "ANE.I",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LIJ4N4R5XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-07-2023_Bibliographic Data Sheet",
#       "documentIdentifier": "LIJ4N4R7XBLUEX5",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-07-2023",
#       "documentCode": "BIB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Response After Final Action",
#       "documentIdentifier": "LH18TDM2XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "A.NE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Claims",
#       "documentIdentifier": "LH18TDM3XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "CLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Applicant Arguments/Remarks Made in an Amendment",
#       "documentIdentifier": "LH18TDM4XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "REM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LH18TDM6XBLUEX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_04-28-2023_Fee Worksheet (SB06)",
#       "documentIdentifier": "LH6PHPY6XBLUEX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "04-28-2023",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Final Rejection",
#       "documentIdentifier": "LEN8UO5OGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "CTFR",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_List of references cited by examiner",
#       "documentIdentifier": "LEN8UO5PGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "892",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Search information including classification, databases and other search related notes",
#       "documentIdentifier": "LEN8UO5QGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "SRFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Index of Claims",
#       "documentIdentifier": "LEN8UO5RGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "FWCLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Bibliographic Data Sheet",
#       "documentIdentifier": "LEN8UO5SGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "BIB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LEN8UO5TGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_List of References cited by applicant and considered by examiner",
#       "documentIdentifier": "LEN8UO5UGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "1449",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LEN8UO5WGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-01-2023_Examiner's search strategy and results",
#       "documentIdentifier": "LEN8UO5XGREENX0",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-01-2023",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Information Disclosure Statement (IDS) Form (SB08)",
#       "documentIdentifier": "LBH6XQFFXBLUEX2",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "IDS",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Fee Worksheet (SB06)",
#       "documentIdentifier": "LBH6XQFHXBLUEX2",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LBH6XQFIXBLUEX2",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Amendment/Request for Reconsideration-After Non-Final Rejection",
#       "documentIdentifier": "LBH6MZOHXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "A...",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Claims",
#       "documentIdentifier": "LBH6MZOJXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "CLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Applicant Arguments/Remarks Made in an Amendment",
#       "documentIdentifier": "LBH6MZOKXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "REM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "LBH6MZOLXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_12-09-2022_Fee Worksheet (SB06)",
#       "documentIdentifier": "LBPRSQA5XBLUEX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "12-09-2022",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Non-Final Rejection",
#       "documentIdentifier": "L7S01XN8XBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "CTNF",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_List of references cited by examiner",
#       "documentIdentifier": "L7S01XN9XBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "892",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Index of Claims",
#       "documentIdentifier": "L7S01XNAXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "FWCLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Search information including classification, databases and other search related notes",
#       "documentIdentifier": "L7S01XNBXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "SRFW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_List of References cited by applicant and considered by examiner",
#       "documentIdentifier": "L7S01XNCXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "1449",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Examiner's search strategy and results",
#       "documentIdentifier": "L7S01XNDXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Bibliographic Data Sheet",
#       "documentIdentifier": "L7S01XNEXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "BIB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-09-2022_Examiner's search strategy and results",
#       "documentIdentifier": "L7S01XNGXBLUEX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-09-2022",
#       "documentCode": "SRNT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-15-2021_Information Disclosure Statement (IDS) Form (SB08)",
#       "documentIdentifier": "KPYPADO1DFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-15-2021",
#       "documentCode": "IDS",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_06-15-2021_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "KPYPADO5DFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "06-15-2021",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_03-25-2021_Notice of Publication",
#       "documentIdentifier": "KMP4JFS0DFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "03-25-2021",
#       "documentCode": "NTC.PUB",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-30-2020_Fee Worksheet (SB06)",
#       "documentIdentifier": "KFO0PJ8TLDFLYX9",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-30-2020",
#       "documentCode": "WFEE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-30-2020_Filing Receipt",
#       "documentIdentifier": "KFO0PIJFDFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-30-2020",
#       "documentCode": "APP.FILE.REC",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Oath or Declaration filed",
#       "documentIdentifier": "KFG167MHRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "OATH",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Drawings-only black and white line drawings",
#       "documentIdentifier": "KFG167MIRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "DRW",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Application Data Sheet",
#       "documentIdentifier": "KFG167MJRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "ADS",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Electronic Filing System Acknowledgment Receipt",
#       "documentIdentifier": "KFG167MKRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "N417",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "OUTGOING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Electronic Fee Payment",
#       "documentIdentifier": "KFG167MLRXEAPX1",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "N417.PYMT",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Specification",
#       "documentIdentifier": "KFI34T7ELDFLYX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "SPEC",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Claims",
#       "documentIdentifier": "KFI34T7FLDFLYX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "CLM",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Abstract",
#       "documentIdentifier": "KFI34T7GLDFLYX4",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "ABST",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INCOMING"
#     },
#     {
#       "bookmarkTitleText": "84561_16948574_09-23-2020_Placeholder sheet indicating presence of supplemental content in Supplemental Complex Repository for Examiners(SCORE)",
#       "documentIdentifier": "KFYBBJL5DFLYX10",
#       "applicationNumberText": "16948574",
#       "customerNumber": "84561",
#       "mailDateTime": "09-23-2020",
#       "documentCode": "SCORE",
#       "mimeCategory": "pdf",
#       "previewFileIndicator": False,
#       "documentCategory": "INTERNAL"
#     }
#   ],
#   "rid": "514c10f5-ff44-4edc-bc41-89d581445c68"
# })
# headers = {
#   'X-INSTANA-L': '1,correlationType=web;correlationId=4ff897daaec603ee',
#   'X-INSTANA-S': '4ff897daaec603ee',
#   'sec-ch-ua-platform': '"Windows"',
#   'X-INSTANA-T': '4ff897daaec603ee',
#   'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
#   'sec-ch-ua-mobile': '?0',
#   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
#   'Accept': 'application/json, text/plain, */*',
#   'DNT': '1',
#   'Content-Type': 'application/json',
#   'Sec-Fetch-Site': 'same-origin',
#   'Sec-Fetch-Mode': 'cors',
#   'Sec-Fetch-Dest': 'empty',
#   'host': 'patentcenter.uspto.gov',
#   'Cookie': 'TS01fadf8b=01874167c7b40f2af6a67337e41e0d0e9a00748ff0dc539b791067e836afe73d1143338094f9aa751d00bfc18a98f6c7ac40c5a4d2; TS457c8013027=08591d7655ab2000e30446d7b63036a42e0a36cda39050608b45b10804444242cbf2832665ff4e24083f931f161130006bddfd067fe4a3471177fc6dfc327003b65c14f6fe94d91f2b262f06778b9207e3f1b96a87b538f8ff1734b2d074a8e8'
# }

# response = requests.request("POST", url, headers=headers, data=payload)

# print(response.text)



model_tools = [
        {
            'type': 'function',
            'function': {
                'name': 'get_apps_by_country',
                'description': 'Get all applications that is filed from a given country code',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'countryCode': {
                            'type': 'string',
                            'description': '2 letters country code e.g. US, JP, VA, etc'
                        }
                    },
                    'required': ['countryCode'],
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_apps_by_case_status',
                'description': 'Get all applications that have a given status',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'status': {
                            'type': 'string',
                            'description': 'Current status of the application'
                        },
                        'year': {
                            'type': 'string',
                            'description': 'Year of the current status date of the application'
                        }
                    },
                    'required': ['status'],
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_app_docs',
                'description': 'Get useful documents of a case or application',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'status': {
                            'type': 'string',
                            'description': 'application Id number'
                        }
                    },
                    'required': ['applId'],
                }
            }
        }
    ]