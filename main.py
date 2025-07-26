from pyzipcode import ZipCodeDatabase
import requests
import json
import re
from APIKeys import googleCivicInfoKey, congressApiKey


url = "https://api.congress.gov/"


global city, state, district, currentCongress, year
currentCongress = 119
zipcodeDatabase = ZipCodeDatabase()

def getZipcode():
    try:
        zipcode = input("Enter zip code: ")
        if zipcode.isalpha():
            return zipcode
    except KeyError as e:
        print(f"{e}")

def zipToCityState(zip):
    global city, state
    try:
        zipInfo = zipcodeDatabase[zip]
        city = zipInfo.city
        state = zipInfo.state
        # test print
        # print(f"The zipcode {zip} corresponds to {city}, {state}")
    except KeyError:
        print("Error with finding corresponding city & state.")

    return city, state

def getCongressionalDistrict(zip, googleCivicApiKey):
    global district
    url = "https://www.googleapis.com/civicinfo/v2/divisionsByAddress"
    params = {
        "key": googleCivicApiKey,
        "address": zip,
        "levels": "country",
        "roles": "legislatorUpperBody,legislatorLowerBody"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # return data
        if "divisions" in data:
            for division_id, info in data["divisions"].items():
                if "cd:" in division_id:
                    # test print
                    #print(f"zip code {zip} translates to {info.get('name')}")
                    districtInfo = info.get('name')
                    districtNum = re.search(r"\b(\d+)(?:st|rd|th|nd)?\b", districtInfo)
                    if districtNum:
                        district = int(districtNum.group(1))
                        # test print
                        # print(f"District: {district}")
                        return district
                    else:
                        print(f"Error finding district for zipcode: {zip}")
    except requests.exceptions.RequestException as e:
        return None

def findPoliticianByState(state):
    results = []
    try:
        response = requests.get(f"https://api.congress.gov/v3/member/{state}?api_key={congressApiKey}")
        response.raise_for_status()
        data = response.json()
        # print(json.dumps(data))
        for member in data.get("members", []):
            name = member.get("name")
            district = member.get("district")
            if not district:
                district = "Senator"
            party = member.get("partyName")
            terms = member.get("terms", "item")
            termInformation = terms["item"][0]
            # print(termInformation)
            startYear = termInformation["startYear"]
            chamber = termInformation["chamber"]
            if "endYear" in termInformation:
                endYear = termInformation["endYear"]
            else:
                endYear = "Present"
            if endYear == "Present":
                # print(f"Name: {name}")
                # print(f"State: {state}")
                # print(f"District: {district}")
                # print(f"Party: {party}")
                # print(f"Chamber: {chamber}")
                # print(f"End Year: {endYear}")
                # print(f"Start Year: {startYear}")
                # print("-"*40)
                results.append({
                    "name": name,
                    "state": state,
                    "district": district,
                    "party": party,
                    "chamber": chamber,
                    "startYear": startYear,
                    "endYear": endYear
                })

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return results

def findPoliticianByDistrict(dist):
    results = []
    try:
        response = requests.get(f"https://api.congress.gov/v3/member/{state}/{dist}?api_key={congressApiKey}")
        response.raise_for_status()
        data = response.json()
        # print(json.dumps(data))
        for member in data.get("members", []):
            name = member.get("name")
            district = member.get("district")
            if not district:
                district = "Senator"
            party = member.get("partyName")
            terms = member.get("terms", "item")
            termInformation = terms["item"][0]
            # print(termInformation)
            startYear = termInformation["startYear"]
            chamber = termInformation["chamber"]
            if "endYear" in termInformation:
                endYear = termInformation["endYear"]
            else:
                endYear = "Present"
            if endYear == "Present":
                results.append({
                    "name": name,
                    "state": state,
                    "district": district,
                    "party": party,
                    "chamber": chamber,
                    "startYear": startYear,
                    "endYear": endYear
                })
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return results

def findYeaOrNay():
    results = []
    sessionNumber = 1
    rollcallNumber = 17
    # testing rollCall at 17
    # sessionNumber is 1 until January 3, 2026
    votingURL = f"https://api.congress.gov/v3/house-vote/{currentCongress}/{sessionNumber}/{rollcallNumber}/members?api_key={congressApiKey}"
    #     session number is usually 1 or 2
    # legislationNumber is the bill number
    response = requests.get(votingURL)
    data = response.json()
    voteInfo = data.get("houseRollCallVoteMemberVotes", [])
    bill = voteInfo.get("legislationNumber")
    results.append("Bill Number: " + bill)
    for result in voteInfo.get("results", []):
        entry = {
            "firstName": result.get("firstName"),
            "lastName": result.get("lastName"),
            "votingResult": result.get("voteCast"),
            "party": result.get("voteParty"),
            "state": result.get("voteState")
        }

        results.append(entry)
    return results






def main2():
    zipcode = getZipcode()
    if zipcode:
        cit,st = zipToCityState(zipcode)
        dist = getCongressionalDistrict(zipcode, googleCivicInfoKey)
        if dist:
            findPoliticianByDistrict(dist)
        if not dist:
            print(f"No current members matching zipcode: {zipcode}. Here are members for the state: {st}")
            findPoliticianByState(st)
    if not zipcode:
        print("Error")

def main():
    re = findYeaOrNay()
    for r in re:
        print(r)





if __name__ == "__main__":
    main()