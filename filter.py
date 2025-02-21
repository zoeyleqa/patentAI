import json
import os
import ijson
import re


inputfile = os.path.join(os.path.dirname(__file__), "jsons\\2023.json")
outputfile = os.path.join(os.path.dirname(__file__), "result.json")
result = []

def get_app_by_country(countryCode): 
    # Open the JSON file
    with open(inputfile, 'r', encoding="utf8") as file:
        # Parse the JSON objects one by one
        parser = ijson.items(file, 'PatentBulkData.item')
        
        # Iterate over the JSON objects
        for i in parser:
            try:
                if(i['patentCaseMetadata']['applicationTypeCategory'] == 'Utility'):       
                    bag = i['patentCaseMetadata']['partyBag']['applicantBagOrInventorBagOrOwnerBag']
                    
                    if any('partyIdentifierOrContact' in d for d in bag):
                        poc = next((j for j,d in enumerate(bag) if 'partyIdentifierOrContact' in d), None)
                    
                        if poc != None and len(bag[poc]['partyIdentifierOrContact']) > 0:
                            pocAddr = bag[poc]['partyIdentifierOrContact'][0]['postalAddressBag']['postalAddress']
                            for contact in pocAddr: 
                                if contact['postalStructuredAddress']['countryCode'] == countryCode:
                                    result.append(i['patentCaseMetadata']['applicationNumberText']['value']) 
                                    break
            except KeyError:
                pass
                # print(i['patentCaseMetadata']['applicationNumberText']['value'])

    # Transform python object back into json
    output_json = json.dumps(result)

    fOut = open(outputfile, 'w', encoding="utf8") 
    fOut.write(output_json)
    fOut.close()

    # Show json
    print("Total result", len(result))


def get_app_by_case_status(status):
    # Open the JSON file
    with open(inputfile, 'r', encoding="utf8") as file:
        # Parse the JSON objects one by one
        parser = ijson.items(file, 'PatentBulkData.item')
        
        # Iterate over the JSON objects
        for i in parser:
            try:
                if re.search(status, i['patentCaseMetadata']['applicationStatusCategory']):       
                    result.append(i['patentCaseMetadata']['applicationNumberText']['value']) 
                    print(i['patentCaseMetadata']['applicationNumberText']['value'] + ' - ' + i['patentCaseMetadata']['applicationStatusCategory'])
                    
            except KeyError:
                pass
                # print('error - ' + i['patentCaseMetadata']['applicationNumberText']['value'])

    # Transform python object back into json
    output_json = json.dumps(result)

    fOut = open(outputfile, 'w', encoding="utf8") 
    fOut.write(output_json)
    fOut.close()

    # Show json
    print("Total result", len(result))


def get_app_by_appl_id(applId):
    # Open the JSON file
    with open(inputfile, 'r', encoding="utf8") as file:
        # Parse the JSON objects one by one
        parser = ijson.items(file, 'PatentBulkData.item')
        
        # Iterate over the JSON objects
        for i in parser:
            try:
                if i['patentCaseMetadata']['applicationNumberText']['value'] == applId:       
                    print(i)
                    break
                    
            except KeyError:
                pass
                # print('error - ' + i['patentCaseMetadata']['applicationNumberText']['value'])

    # Transform python object back into json
    # output_json = json.dumps(result)
    # print(output_json)
    # fOut = open(outputfile, 'w', encoding="utf8") 
    # fOut.write(output_json)
    # fOut.close()



if __name__ == "__main__":
    # sys.exit(main())
    # get_app_by_case_status('Abandoned')
    get_app_by_appl_id('09233249')