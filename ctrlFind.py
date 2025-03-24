from bs4 import BeautifulSoup as BS
from bs4 import NavigableString
import requests
import pprint
import re
import argparse

pp = pprint.PrettyPrinter(indent=4)

globalStorage = []

def processCapture(elementArray):
	res = []
	i = 0	
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

			individualName += array[index] + " "
			#Names can have multiple or single tags
			index += 1
		tempDictionary["name"] = [individualName.strip()]
	
	else:
		while array[index] != "Name Type:":
			PrimaryNameMatcher = re.match("Primary Name", array[index])
			AliasMatcher = re.match("Primary Name", array[index])
			if (not PrimaryNameMatcher and not AliasMatcher):
				individualName += array[index] + " "
			index += 1
		tempDictionary["name"].append(individualName.strip())
	
	return (tempDictionary, index)


def dictify(arr):
	tempD = dict()
	i = 0
	while i < len(arr):
		
		uniqueIdMatch = re.fullmatch("Unique ID:", arr[i])
		
		if (uniqueIdMatch):
			tempD["id"] = arr[i + 1]
			tempD["type"] = arr[i + 2]
			i += 2

		#Since everything here on has a lookahead
		elif ((i + 1) < len(arr)):
			a = arr[i].split('Name:')
			pattern = "Name:"
			t = re.fullmatch(pattern, arr[i])

			#Either we get a pattern match of whole word or None
			if (t):

				if tempD["type"] and tempD["type"] != "Individual":
					if "name" not in tempD:
						tempD["name"] = [arr[i + 1]]
					else:
						tempD["name"].append(arr[i + 1])
						i += 1

				if tempD["type"] == "Individual":
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

				globalStorage.append(tempD)
				tempD = {}
				i += 1

			#For the very last element	
			elif ((i + 1) >= len(arr)):

				globalStorage.append(tempD)
				tempD = {}
				i += 1

			else:
				i += 1

		#normal increment
		else:
			i += 1


def load():
	source = requests.get("https://docs.fcdo.gov.uk/docs/UK-Sanctions-List.html").text[:]
	soup = BS(source, "lxml")
	capturedDivs = soup.find_all("div")[1:]
	processedElements = processCapture(capturedDivs)
	dictify(processedElements)


def search(keyword: str, searchType: str):
	result: (str, str, str) = []
	for i in globalStorage:
		for j in i["name"]:
			match = re.search(keyword, j) if searchType == "substring" else re.match(keyword, j)
			if (match):
				result.append((i["id"], i["type"], keyword))
				break
			else:
				pass

	return result


def main():
	parser = argparse.ArgumentParser(description='Find Unique ID, Name and Type from UK Sanctions List')
	parser.add_argument('--keyword', type=str, nargs="+", help="a keyword/name to search for")
	parser.add_argument('--searchType', choices=["substring", "start"], default="substring")
	args = parser.parse_args()
	keyword = args.keyword
	searchType = args.searchType

	try:
		word = " ".join(keyword)
		print ("Searching for: ", word)
		print ("Search Type: ", searchType)

		boolArrayAlpha = [x.isalpha() for x in keyword]

		if (all(boolArrayAlpha)):
			load()
			result = search(word, searchType)
			if not result:
				print ("No results found!")
			else:
				pp.pprint(result)
		else:
			print ("Please provide a valid string that only contains letters")
	
	except Exception as e:
		print (e)


if __name__ == "__main__":
	main()


