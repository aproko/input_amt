from os import listdir
from os.path import isfile, join
from nltk.stem import WordNetLemmatizer
import csv
import sys
import codecs
import random
from bs4 import BeautifulSoup


listoflines = []
part_listoflines = []
part_uncert = []
uncert = []
dict = {}
multi_dict = {}
total_dict = {}
hedge_counts = {}
gold_qs = []

#Input directory is where the cleaned up .Anno files are located
#numSentPerHIT is how many questions are asked in each HIT (usually 10)
#partitionNum is maximally how many instances of each hedge we want to appear the AMT dataset
#totalEx is the total number of examples we want in the datasheet

input_directory = sys.argv[1]
numSentPerHIT = int(sys.argv[2])
partitionNum = int(sys.argv[3])
totalEx = int(sys.argv[4])


lemmatizer = WordNetLemmatizer()

#Dictionary is in the format: hedge, type of hedge, definition of that type of hedge, the hedging definition of that word, the hedging example of that word, the non-hedging definition of that word, the non-hedging example of that word

def readIn(filename, mode):
    with codecs.open(filename, 'rU', encoding='utf-8') as inputFile:
        reader = csv.reader(inputFile)
        next(reader, None)
        for line in reader:
            if mode == "gold":
                gold_qs.append(line)
            else:
                entry = [line[1], line[2], line[3], line[4], line[5], line[6]]
                if mode == "dict":
                    dict_lemma = lemmatizer.lemmatize(line[0])
                    dict[dict_lemma] = entry
                elif mode == "multi":
                    multi_dict[line[0]] = entry

def findHedges(id, orig_sentence, sentence, mode, total_dict):
    words = sentence.split()
    orig_word = ""
    
    #If we're looking for multi-word hedges, we add all potential ngrams (up to 6) that could be in the sentence to the list of words
    if mode == "multi":
        dictionary = multi_dict.copy()
        words = orig_sentence.split()
        sentence_length = len(orig_sentence.split())
        maxlength = min(6, sentence_length)
        for start in range(sentence_length):
            potential_multiword = words[start]
            
            for length in range(1, min(maxlength, sentence_length - start)):
                potential_multiword = " ".join([potential_multiword, words[start+length]])
                words.append(potential_multiword)
    
    elif mode == "single":
        dictionary = dict.copy()
        
    multi_line = sentence
                                
    for word_index in range(0,len(words)):    #)word in words:
        word = words[word_index]
        if word_index > 0:
            prev_word = words[word_index - 1]
        else:
            prev_word = ""
        if mode == "single":
            orig_word = str(word)
            word = lemmatizer.lemmatize(word)
                                
        if word in dictionary and prev_word != "to" and prev_word != "you":
            entry = id + ",\"" + orig_sentence + "\"," + word + "," + ",".join(dictionary[word])
            listoflines.append(entry)
                            
            #We replace all multi-word hedges with "0" in order to not identify potential single hedge words within multi-word expressions.
            if mode == "multi":
                multi_line = multi_line.replace(word, "0")


            if total_dict[word] > 0 and entry not in gold_qs and len(part_listoflines) < totalEx:
                part_listoflines.append(entry)
                total_dict[word] -= 1
        
            #We increment the count
            if word in hedge_counts:
                hedge_counts[word] += 1
            else:
                hedge_counts[word] = 1

    return multi_line

def output(filename, listToPrint, mode):
    if mode == "defs":
        header_defs="sentenceID0,sentence0,hedge0,hedgeType0,defHedgeType0,hedgingDef0,hedgingEx0,nonHedgeDef0,nonHedgeEx0,answer"
            
        for i in range(1,numSentPerHIT):
            header_defs = header_defs + ",sentenceID" +str(i) + ",sentence"+ str(i)+",hedge"+str(i)+",hedgeType"+str(i)+",defHedgeType"+str(i)+",hedgingDef"+str(i)+",hedgingEx"+str(i)+",nonHedgeDef"+str(i)+",nonHedgeEx"+str(i)

    elif mode == "uncert":
        header_defs = "sentenceID0,sentence0"
            
        for x in range(1,numSentPerHIT):
            header_defs = header_defs + ",sentenceID" + str(x) + ",sentence"+str(x)


    with codecs.open(filename, 'w', encoding='utf-8') as out_defs:
        out_defs.write(header_defs)
        out_defs.write("\n")
            
        b = 0
        temp_defs = ""
        count = 0
        gold = list(gold_qs)
            
        for item in listToPrint:
            #if mode == "defs":
            if 1 == 1: #too lazy to re-indent everything
            #if count < (totalEx // numSentPerHIT):
                if b == 0:
                    if mode == "defs":
                        temp_defs = ",".join(random.choice(gold))
                    elif mode == "uncert":
                        temp_defs = item
                    b += 1
                if b < numSentPerHIT and b > 0:
                    temp_defs = temp_defs + "," + item
                    b += 1
                if b == numSentPerHIT:
                    out_defs.write(temp_defs)
                    out_defs.write("\n")
                    b = 0
                    count += 1
        if b != 0:
            out_defs.write(temp_defs)
            out_defs.write("\n")
                       
    
    


def partitionUncert():
    while len(part_uncert) < totalEx:
        temp_unc = random.choice(uncert)
        while temp_unc in part_uncert:
            temp_unc = random.choice(uncert)
        part_uncert.append(temp_unc)

        random_hedged = random.choice(part_listoflines)
        temp_random_hedged = random_hedged.split(",")
        temp_random_hedged_part = temp_random_hedged[0] + "," + temp_random_hedged[1]
    
        while temp_random_hedged_part in part_uncert:
            random_hedged = random.choice(part_listoflines)
            temp_random_hedged = random_hedged.split(",")
            temp_random_hedged_part = temp_random_hedged[0] + "," + temp_random_hedged[1]
        part_uncert.append(temp_random_hedged_part)



def main():
    
    readIn('dictionary.csv', "dict")
    readIn('multiword_dict.csv', "multi")
    readIn('amt_check_questions.csv', "gold")
    
    onlyfiles = [ f for f in listdir(input_directory) if (isfile(join(input_directory,f)) and ".toAnno.txt" in f) ]

#This lets us keep track of the number of instances of each word in our datasheet
    joined_list = dict.keys() + multi_dict.keys()
    total_dict = dict.fromkeys(joined_list, partitionNum)

    for files in onlyfiles:
    
    #Files are in the format: sentenceID, sentence
        soup = BeautifulSoup(open(join(input_directory, files)), "lxml")
        paragraph = soup.get_text()
        paragraph = paragraph.strip()
        para_list = paragraph.split("\n")

        for lines in para_list:
            id_and_line = lines.split("::")
            line = id_and_line[1]
            id = id_and_line[0]
            
            #Checking again that sentences are at least 3 words long.
            if len(line.split()) > 2:
                #For the uncertainty determination and confidence level datasheet, we just need the sentence which will be annotated
                #uncert.append(id + ",\""+line + "\"")
                multi_line = findHedges(id, line, line, "multi", total_dict)
                temp_str = findHedges(id, line, multi_line, "single", total_dict)

    if totalEx < len(uncert):
        partitionUncert()


    output('amt_input_defs_ex_lem.csv', listoflines, "defs")
    #output('amt_input_unc_lem.csv', uncert, "uncert")
#  output('amt_input_defs_examples_lem_PART.csv', part_listoflines, "defs")
#   output('amt_input_uncert_lem_PART.csv', part_uncert, "uncert")

    with codecs.open('amt_hedge_counts.csv', 'w', encoding='utf-8') as data_out:
        for hedge, counts in hedge_counts.items():
            data_out.write(",".join([hedge, str(counts)]))
            data_out.write("\n")

main()

