#!bin/bash


    while getopts 'cda*' flag; do
        case "${flag}" in
            #$2 is the directory with the text files in .cmp.txt format
            c) python clean_text.py "$2"; echo "Cleaning Input Text" ;;
            #$2 is the directory with the text files in .toAnno.txt format
            #$3 is the number of sentences per HIT to be put in the datasheet
            #$4 is the max number of times a hedge should appear in the dataset
            #$5 is the total number of sentence we want to use
            d) python create_datasheet.py "$2" "$3" "$4" "$5"; echo "Creating Datasheet" ;;
            a) python clean_text.py "$2"; python create_datasheet.py "$2" "$3" "$4" "$5"; echo "Running the entire pipeline" ;;
        esac
    done

