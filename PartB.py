from PartA import tokenize, computeWordFrequencies
import sys

#The time complexity of the main function is O(n) due to looping through all tokens to check for 
#common tokens in the other file. This is not O(n^2) because I use the fact that dictionaries use 
#hashtables for O(1) lookup and only look through 1 file and lookup the other as a dictionary
#this is also not O(nlogn) becuase the print function from part a is not used, also tokenize
#and computewordfrequencies are O(n), please see parta for details on those functions.
#The output of common words way be larger than expected due to tokenization decisions, such as keeping
#tokens with length <3 since they could be potentilly significant such as bi and a
def main():
    if(len(sys.argv) < 3):
        print("Not all files provided in command line, please try again")
        return
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]

    try:
        tokens_1 = tokenize(file1)#O(n)
    except Exception as e:
        print(f'Aborting Tokenization, error detected during reading of file1: {e}')
        return
    try:
        tokens_2 = tokenize(file2)#O(n)
    except Exception as e:
        print(f'Aborting Tokenization, error detected during reading of file2: {e}')
        return


    file1_tokens = (computeWordFrequencies(tokens_1)).keys() #to iterate through O(n), .keys() is a O(1) operation
    file2_tokens = computeWordFrequencies(tokens_2) #to do O(1) key lookup

    counter = 0
    print("Common tokens between files:")
    for i in file1_tokens: #performs this task in O(n) and not O(n^2) becuase file_2 uses a hashtable
        if i in file2_tokens: #O(1) lookup since python dict uses hashtable and in uses this
            print(i)
            counter = counter + 1
    print()
    print("Number of common tokens between files")
    print(counter) #ends as O(n)


if __name__ == "__main__":#entry point of program
    main()
