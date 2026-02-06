import sys #for use in command line

#List<Token> tokenize(TextFilePath)
"""
This is the assumption I made given the above signature:
return a list of 'Tokens', these could be either strings or Token objects
of a Token class, after speaking with a TA they suggested either would work, so I will use strings.
the name of the function is tokenize and recieves a textfilepath parameter which is most
likely a string file path from the command line.
"""

"""
----------------Tokenization Decisions-------------------
    From the project write up a token is defined as follows:
    "a token is a sequence of alphanumeric characters, independent of capitalization"
    later on this definition is expanded upon to include:
    "An example of bad input would be a character in a non-English language."
    Ed-discussion post #7 expands this definition to include accented letters as invalid input (endorsed by staff)
    Therefore the definition of a token in this assignment is as follows:

    "A token is a base english ascii sequence of aphanumeric characters, independendent of capitalization, excluding accented letters, latin characters, and symbols"

    Now how should we decide what to do based on certain invalid input?
    The project writeup is not specific on how to handle tokens with invalid input so there are two potential ways to handle them:

    1. throw out entire tokens that contain invalid characters
    pros/cons:
        Will allow all tokens to contain valid characters
        Prevents broken words from being included in tokenization
        MAJOR loss of information on words that contain accented letters or punctuation: jalapeno, 192.159.228
        Entire words are removed due to a single invalid character
    
    2. Skip invalid characters and allow broken tokens, due to ediscussion #37 this leads to splits
    pros/cons:
        Potentially includes additional tokens that arent spelled correctly
        SAVES partial context of the original word for indexing, 
        ex. an entire document talking about a jalapeno recipe still has "jalape o" for context rather than removing the entire word
        Seperates tokens where invalid characters are detected, skipping the invalid chars but potentially saving valid tokens
        ex. don't -> don t which is potentially valid
        ex. hello&^$&*()world would be discarded by choice 1 but kept here as "hello" "world"

    also due to eddiscussion #37 any punctuation isnt alphanumeric and would split tokens, this inludes apostrophies '

    Lastly there is also a decision to be made on what length tokens are allowed
    Early tokenizers only allowed tokens with length > 2
    My tokenizer will allow any length tokens, this includes tokens with length < 3
    My reasoning is that certain words and numbers would be excluded and thus the indexer would lose context for example from lecture:
    "Bigcorp's 2007 bi-annual report showed profits rose 10%.” -> bigcorp 2007 annual report showed profits rose” under early tokenization loses context
    Instead my tokenizer would do the following:
    bigcorp s 2007 bi annual report showed profits rose 10 - which retains a lot more context since it includes shorter tokens that have actual semantic meaning.
    The only thing here it didnt retain was % becuase this doesnt fall in our token definition above.
    This also allow length 1 words such as "a"

    I have made the decisions to follow through with choice 2 as it will preserve word context through invalid characters and maintain Recall.
    It will also allow for a more robust tokenizer as punctuation defines token boundaries.
    Non-English characters are ignored and treated as boundaries to ensure the tokenizer does not fail or discard surrounding
    valid alphanumeric content when encountering invalid input, as required by the project specification.
"""

# Time complexity of this function is O(n) The tokenizer iterates over each character in the file exactly once,
# performing only O(1) operations per character (including appending valid characters, checking split characters, and flushing tokens), 
# so the total runtime is O(n), where n is the total number of characters in the file.
# To see the complexity of certain lines please see the comments below:
def tokenize(TextFilePath: str):#outputs a list of tokens from the file
    tokens = []
    token_chars = []#to avoid O(n^2) from token += char
    is_empty = True  #flag to detect empty files

    with open(TextFilePath, "r", encoding = "utf-8", errors = "replace") as file: #used instead of read and readlines since those read the entire file into memory
        #changed the parameters of open so that different command lines wouldnt crash if they had no knowledge of chars
        for line in file: #look at each line as its read into memory instead of reading entire file
            is_empty = False
            token_chars.clear()
            for char in line:#this is hierarchical so its not O(n^2) but instead O(n), n = #of chars in file but are seperated for k lines: n = k1 + k2 ..., the rest is O(1)
                if(char.isalnum() and char.isascii()): #does not take accented characters or non-english as specified in ed discussion
                    token_chars.append(char.lower())#take the lowercase of all tokens
                else:
                    #split on invalid chars as stated in ed-discussion
                    if token_chars: #dont add empty strings, if we have a current token
                        tokens.append(''.join(token_chars))#add this valid token to the list
                        token_chars.clear()
            if token_chars:#make sure to grab tokens at the end of lines
                tokens.append(''.join(token_chars))
                token_chars.clear()#reset to not double count last word
    if is_empty:#allows the tokenizer to still run if no tokens are generated
        return tokens
    if(len(token_chars) > 0):#token from before end of file if a token was being formed
        tokens.append(''.join(token_chars))
    return tokens #returns a list of strings aka tokens

#Map<Token,Count> computeWordFrequencies(List<Token>)
"""
    My assumptions made about this signature is that it takes a list of tokens as a parameter, 
    in the case of the previous function this will be a list of strings.
    Its output is a mapping of tokens to counts, therefore im assuming
    that mapping is a dictionary where token strings as keys are mapped
    to counts as integer values.
"""

#The time complexity of this function is O(n) since we need to loop through the list to count frequencies, this is the best 
# runtime complexity we can achieve without an imported counter. O(1) operations in the loop
def computeWordFrequencies(token_list: list[str]): #This is O(n) due to loop with O(1) dict additions
    frequencies = {}
    for token in token_list:
        frequencies[token] = frequencies.get(token, 0) + 1 #if the frequencies doesnt exist it adds it with count 0
    return frequencies

#void print(Frequencies<Token, Count>)
"""
    My assumptions made about this signature is that it takes a Frequency mapping of tokens to counts.
    From the previous function I am assuming this is a dictionary of strings mapped to integers.
    Its return type is void so it only prints out the mapping of tokens in the specified manner.
    Specifically I have chosen to print this mapping using the "<token> = <freq>" format.
    As discussed on ed-discussion pythons print() function will collide with this signatures name,
    therefore I have chosen to call it print_frequencies.
"""
# The time complexity of this function is O(nlogn), this comes from sorting the dictionary in descending order.
# Pythons sorted() function uses a hybrid timesort algorithm that is O(nlogn) in worst case. All other operations
# are either O(1) or O(n) so O(nlogn) dominates, please look at comments below for line specific complexity.
def print_frequencies(frequencies: dict[str, int]):#takes in a mapping of frequencies tokens->count
    #sort by decreasing frequency
    descending_frequency = sorted(frequencies.items(), key=lambda item: item[1], reverse=True)#this is O(nlogn), bucket sort would get O(n^2) worst case, our worst here is nlog(n)
    #lambda is O(1), reverse is O(n)
    for key, value in descending_frequency:# O(n)
        print(f'{key} = {value}')# as specified <token> = <freq>

#Time complexity of the main function is O(nlogn) due to the sorting of the dictionary in the print_frequencies function
#Please see that functions time complexity explanation.
def main():
    if len(sys.argv) > 1: #potentially valid file path detected
        #run code normally
        try:
            tokens = tokenize(sys.argv[1])#the filepath from command line
        except Exception as e:
            print(f'Aborting Tokenization, error detected during reading of the file: {e}')
            return
        frequency = computeWordFrequencies(tokens)
        print_frequencies(frequency)
    else:
        print("Input for command line was empty, no absolute path or filename was provided. Please try again")
        return

if __name__ == "__main__":#entry point of code
    main()