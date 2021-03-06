#!/usr/bin/env python2

import os
import random

sampleSize = 100
acc = 0.0
old = ['sentinel']

ironic = [] 
regular = []

files = os.listdir('corpus/Ironic')

for file in files:
	if file.endswith('.txt'):
		ironic.append(file)

files = os.listdir('corpus/Regular')

for file in files:
	if file.endswith('.txt'):
		regular.append(file)

for i in range(sampleSize):
	irony = random.randint(0,1)

	testFile = 'sentinel'
	while testFile in old:
		if irony:
			testFile = random.choice(ironic)
		else:
			testFile = random.choice(regular)
	old.append(testFile)

	if irony:
		f = open('corpus/Ironic/' + testFile)
	else:
		f = open('corpus/Regular/' + testFile)

	reviewFlag = 0
	for row in f:
		# print row
		# look for the start of the actual review...
		if row == '<REVIEW>\n':
			reviewFlag = 1
			continue
			# print 'hi'
		# then start parsing
		if reviewFlag == 1:
			if row != '</REVIEW>':
				print row

	response = ''
	while response not in ['y', 'n']:
		response = raw_input("Is the above sarcastic? (y/n)\n")

		if response == 'y':
			humanChoice = 1
		elif response == 'n':
			humanChoice = 0
		else:
			print 'Invalid response.'

	if (irony + humanChoice) % 2 == 0:
		print '\n\nCorrect!\n\n'
		acc += 1.0 / sampleSize
	else:
		print '\n\nIncorrect.\n\n'

	f.close()

print 'Test complete. Human-assessed accuracy was ' + str(acc) + '.'
