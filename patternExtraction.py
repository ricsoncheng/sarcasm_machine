import numpy as np
import os
import re

def parse_nopunc(inp):
	#Does not cosinder punctuation
	reviewFlag = 0
	parsed_inp = []
	for row in inp:
		# print row
		# look for the start of the actual review...
		if row == '<REVIEW>\n':
			reviewFlag = 1
			continue
			# print 'hi'
		# then start parsing
		if reviewFlag == 1:
			if row != '</REVIEW>':
				line = re.split(' |\.|\,|\!|\?|\/|\(|\)|\-|\_|\\\\|\@|\#|\$|\%|\^|\&|\*|\=|\+|\[|\]|\{|\}|\;|\:|\>|\<|\~', row)
				# print line
				for word in line:
					# if word.find('emoticon') != -1:
						# print word
					word = word.lower().strip('`~!@#$%^&*()-_=+[]}{\\|\'\";:/?.>,<\n')
					if word != '':
						parsed_inp.append(word)
	return parsed_inp
FC=200
FH=20


def constructDict():
	wordCount = 0
	ironic = os.listdir('corpus/Ironic')
	regular = os.listdir('corpus/Regular')
	wordDict = dict()
	for ironicFile in ironic:
		if ironicFile.endswith('.txt'): 
			f = open('corpus/Ironic/' + ironicFile)
			sentence = parse_nopunc(f)
			for word in sentence:
				wordCount+=1
				if word in wordDict:
					wordDict[word]+=1
				else:
					wordDict[word]=1
	for regularFile in regular:	
		if regularFile.endswith('.txt'):
			f = open('corpus/Regular/' + regularFile)
			sentence = parse_nopunc(f)
			for word in sentence:
				wordCount+=1
				if word in wordDict:
					wordDict[word]+=1
				else:
					wordDict[word]=1
	HFWdict = dict()
	CWdict = dict()
	for word in wordDict:
		if wordDict[word]>= FC:
			HFWdict[word] = wordDict[word]
		if wordDict[word]<= FH:
			CWdict[word] = wordDict[word]
	return HFWdict,CWdict




HFWSLOTUB = 6
CWSLOTUB = 5

def findPatterns(HFWdict,CWdict):
	patternDict = dict()
	ironic = os.listdir('corpus/Ironic')
	regular = os.listdir('corpus/Regular')
	count = 0
	for ironicFile in ironic:
		if ironicFile.endswith('.txt'): 
			f = open('corpus/Ironic/' + ironicFile)
			sentence = parse_nopunc(f)
			patterns=get_pattern(sentence,HFWdict,CWdict)
			for pattern in (patterns):
				if pattern in patternDict:
					patternDict[pattern] +=1
				else:
					patternDict[pattern] = 1 
			count+=1
	for regularFile in regular:	
		if regularFile.endswith('.txt'):
			f = open('corpus/Regular/' + regularFile)
			sentence = parse_nopunc(f)
			patterns=get_pattern(sentence,HFWdict,CWdict)
			for pattern in (patterns):
				if pattern in patternDict:
					patternDict[pattern] +=1
				else:
					patternDict[pattern] = 1 
	freqPatternDict = dict()
	for pattern in patternDict:
		if patternDict[pattern]>=20:
			freqPatternDict[pattern] = patternDict[pattern]
	return freqPatternDict

def get_pattern(sentence,HFWdict,CWdict):
	patternList = []
	tag = []
	for word in sentence:
		if word in HFWdict:
			tag.append(word)
		if word in CWdict:
			tag.append('CW')
	i = 0
	while i<len(tag):
		if tag[i]=='CW':
			i+=1
		else:
			hfwcount=1
			cwcount=0
			j=i+1
			tempPattern = tag[i]
			while (hfwcount<=HFWSLOTUB) and (cwcount<=CWSLOTUB) and (j<len(tag)):
				tempPattern=tempPattern+' '+tag[j]
				if tag[j]!='CW':
					cwcount+=1
					patternList.append(tempPattern)
				else:
					hfwcount+=1
				j+=1
		i+=1
 	return patternList


#HFWdict,CWdict=constructDict()
#patterns = findPatterns(HFWdict,CWdict)

def exactMatch(pattern,tag):
	return (pattern in (" ".join(tag)))

def sparseMatch(pattern,tag):
	pattern = pattern.split(" ")
	i = 0
	j = 0
	falseCounter = 0
	while (i<len(tag)) and (falseCounter<2) and (j<len(pattern)):
		if tag[i]==pattern[j]:
			i+=1
			j+=1
		else:
			falseCounter+=1
			i+=1
			while (i<len(tag)):
				if tag[i]!=pattern[j]:
					i+=1
				else:
					i+=1
					j+=1
					break
	if j==len(pattern):
		return (1,0.1) #alpha=0.1
	else:
		return (0,0)

def incomMatchHelper(word,tag,i):
	while i<len(tag):
		if tag[i]==word:
			return True
		else:
			i+=1
	return False

def incomMatch(pattern,tag):
	pattern = pattern.split(" ")
	matching = 0
	i = 0
	j = 0
	while (i<len(tag)) and (j<len(pattern)):
		if tag[i]==pattern[j]:
			i+=1
			j+=1
			matching+=1
		else:
			i+=1
			if incomMatchHelper(pattern[j],tag,i):
				i+=1
				j+=1
				matching+=1
			else:
				j+=1
	if matching==0:
		return (0,0)
	else:
		return (1,float(matching)/len(pattern)*0.1)


def get_pattern_vector(f,sortedPatternDict,HFWdict,CWdict,keylist):
	sentence = parse_nopunc(f)
	tag = []
	vector = []
	for word in sentence:
		if word in HFWdict:
			tag.append(word)
		if word in CWdict:
			tag.append('CW')
	for i in keylist:
		pattern = i
		if exactMatch(pattern,tag):
			vector.append(1)
		elif sparseMatch(pattern,tag)[0]:
			vector.append(sparseMatch(pattern,tag)[1])
		elif incomMatch(pattern,tag)[0]:
			vector.append(incomMatch(pattern,tag)[1])
		else:
			vector.append(0)
	return vector


def set_features(patternDict,HFWdict,CWdict):
	ironic = os.listdir('corpus/Ironic')
	regular = os.listdir('corpus/Regular')
	keylist = patternDict.keys()
	corpus_list = []
	for ironicFile in ironic:
		if ironicFile.endswith('.txt'): 
			f = open('corpus/Ironic/' + ironicFile)
			patternVector = get_pattern_vector(f,patternDict,HFWdict,CWdict,keylist)
			corpus_list.append(patternVector)
	for regularFile in regular:	
		if regularFile.endswith('.txt'):
			f = open('corpus/Regular/' + regularFile)
			patternVector = get_pattern_vector(f,patternsDict,HFWdict,CWdict,keylist)
			corpus_list.append(patternVector)
	return corpus_list


HFWdict,CWdict=constructDict()
patternsDict = findPatterns(HFWdict,CWdict)
corpus_pattern_features = set_features(patternsDict,HFWdict,CWdict)
np.save('corpus_pattern_features',corpus_pattern_features)