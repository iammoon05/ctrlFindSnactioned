from bs4 import BeautifulSoup as BS
from bs4 import NavigableString
import requests
import pprint
import re

pp = pprint.PrettyPrinter(indent=4)

source = requests.get("https://docs.fcdo.gov.uk/docs/UK-Sanctions-List.html").text[:]

soup = BS(source, "lxml")

sampleDict = {
	"id": 1,
	"type": "Entity",
	"names": [("name", "primary"), ("name", "alias"), ("name", "nonlatin")],
	"addresses": [],
	"countries": [],
	"phoneNumbers": [],
	"emails": []
}

globalDB = []

cap = soup.find_all("div")
print(len(cap))

excludingFirst = cap[1:]

def processCapture(elementArray):
	res = []
	i = 0	
	print (len(elementArray))
	while(i < len(elementArray)):
		for child in elementArray[i].descendants:
			if isinstance(child, NavigableString):
				stripChild = child.string.strip()
				if ("Entity" or "Individual" in stripChild):
					stripChild = stripChild.replace("-", "").strip()
				if (stripChild != '' and stripChild != ','):
					res.append(stripChild)
		i += 1
	return (res)

def processIndividualsNames(tempDictionary, array, index, individualName = ""):
	if "name" not in tempDictionary:
		while array[index] != "Name Type:":

			# print (j)
			print (array[index])
			individualName += array[index] + " "
			#Names can have multiple or single tags
			index += 1
		print ('done with frst ever name: ' + individualName)
		tempDictionary["name"] = [individualName.strip()]
		print(tempDictionary)
	else:
		print ('while name exists in dict')
		print (array[index])
		while array[index] != "Name Type:":
			PrimaryNameMatcher = re.match("Primary Name", array[index])
			AliasMatcher = re.match("Primary Name", array[index])
			if (not PrimaryNameMatcher and not AliasMatcher):
				individualName += array[index] + " "
			index += 1
		# print ('done with additonal names: ' + individualName)
		tempDictionary["name"].append(individualName.strip())
	print (index)
	return (tempDictionary, index)


def dictify(arr):
	tempD = dict()
	i = 0
	individualName = ""
	while i < len(arr):
		print ('element: ' + arr[i])
		
		uniqueIdMatch = re.fullmatch("Unique ID:", arr[i])
		entityTypeMatch = re.fullmatch("Entity", arr[i])
		individualTypeMatch = re.fullmatch("Individual", arr[i])
		
		if (uniqueIdMatch):
			tempD["id"] = arr[i + 1]
			tempD["type"] = arr[i + 2]
			i += 2

		#Since everything here on has a lookahead
		elif ((i + 1) < len(arr)):
			print ('tried in lookahead')
			a = arr[i].split('Name:')
			pattern = "Name:"
			t = re.fullmatch(pattern, arr[i])
			if (t):
				print ('Got into name')
				print (tempD)

				if tempD["type"] and tempD["type"] != "Individual":
					if "name" not in tempD:
						tempD["name"] = [arr[i + 1]]
					else:
						tempD["name"].append(arr[i + 1])
						i += 1

				if tempD["type"] == "Individual":
					individualName = ""

					#Since this tag will be Name
					i = i + 1

					tempD, i = processIndividualsNames(tempD, arr, i)

				
			if ("Address Country:" in arr[i]):
				if "country" not in tempD:
					tempD["country"] = [arr[i + 1]]
				else:
					if (arr[i+1]) not in tempD["country"]:
						tempD["country"].append(arr[i + 1])
				i += 1

			
			#Addtional check before doing id lookahead
			if (i != (len(arr) - 1) and "Unique ID:" in arr[i+1]):

				globalDB.append(tempD)
				tempD = {}
				i += 1

			#For the very last element	
			elif ((i + 1) >= len(arr)):

				globalDB.append(tempD)
				tempD = {}
				i += 1

			else:
				i += 1

		#normal increment
		else:
			i += 1

processedElements = processCapture(excludingFirst)

print(processedElements[-1])
dictify(processedElements)
pp.pprint(globalDB)


