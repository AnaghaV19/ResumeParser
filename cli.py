import os
import argparse
from pprint import pprint
from resume_parser import ResumeParser
import multiprocessing as mp

def print_cyan(text):
    print("\033[96m {}\033[00m" .format(text))
def extract_from_directory(file):
    
    path="./resume/"+file
    print("Path in process==",path)
    if os.path.exists(path):
            print_cyan('Extracting data from: {}'.format(path))
            resume_parser = ResumeParser(path)
            return [resume_parser.get_extracted_data()]
    else:
        return 'File not found. Please provide a valid file name.'

def resume_result_wrapper(resume):
    print_cyan('Extracting data from: {}'.format(resume))
    parser = ResumeParser(resume)
    return parser.get_extracted_data()

##if __name__ == '__main__':
##    pprint(extract_from_directory("resume"))
