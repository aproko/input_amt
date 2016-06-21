These scripts create a data sheet that can be submitted to Amazon Mechanical Turk. Note: I have had a lot of errors with encoding and symbols that appear weird because files were opened in Microsoft Excel or on a Windows system at some point. So AMT might reject a data sheet for that reason and you may or may not have to fix the symbols by hand.

To run:

- option 1: if you just want to clean the input text (in a specific directory, all files ending in .cmp.txt) which includes splitting the document into sentences (ignoring sentences less than 3 words long and questions, since we are uninterested in hedge cues appearing in questions) and writing output files with one sentence per line, each with a numeric identifier

bash run.sh -c /directory/with/input/files

- option 2: if you have clean text already (i.e. text in the format of ID::sentence with one sentence per line), and you just want to create an AMT data sheet

bash run.sh -d /directory/with/input/files #sentencesPerHIT maxNumOfTimesAHedgeShouldAppear totalNumberofSentencesToUse

eg. bash run.sh -d /Users/input/folder 10 50 10000

- option 3: if you want to clean the text AND create an AMT data sheet

bash run.sh -a /directory/with/input/files #sentencesPerHIT maxNumOfTimesAHedgeShouldAppear totalNumberofSentencesToUse

eg. bash run.sh -a /Users/input/folder 10 50 10000

- option 3: if you want to 