
import wikipedia

def findWikiEntriesByTag(tag,NUM_TO_GET=1):
	searchEntries = wikipedia.search(tag)

	numFound = 0
	entriesList = []

	for entry in searchEntries:

		lowerEntry = entry.lower()

		if "disambiguation" in entry:continue
		if lowerEntry == tag:continue

		else:
			#get just the first two sentences of the summary
			try:
				summary = wikipedia.summary(entry,sentences=2)
			except:
				continue

			if len(summary) > 200: continue

			#replace the word if its in the summary
			editedSummary = summary.lower().replace(lowerEntry,"X"*len(entry))

			print ("ANSWER:",entry)
			print ("QUESTION: ",editedSummary)

			entriesList.append({entry:editedSummary})
			numFound += 1
			if numFound == NUM_TO_GET:
				return entriesList
	return entriesList

def getWikipediaQuestions(criteria,categories=["Tag"],NUM_TO_GET = 1):
	return findWikiEntriesByTag(criteria,NUM_TO_GET)