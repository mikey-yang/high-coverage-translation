import csv
import functools
import hashlib
import itertools
import json
import os
import random
import re
import sys
from typing import Any, Dict, List, Set, Tuple
import unicodedata


FIELDSEP = "|"

def makeID(text: str) -> str:
    """
    Create a unique ID based on the value of the input text.

    WARNING: This is typically used to create prompt IDs, but
    because of issues with stray spaces in the prompts,
    this may not always produce the ID you are expecting.
    """
    
    textID = hashlib.md5(text.lower().encode()).hexdigest()
    return "prompt_%s"%textID
    
def read_trans_prompts(lines: List[str]) -> List[Tuple[str,str]]:
    """
    This reads a file in the shared task format, returns a list of Tuples containing ID and text for each prompt.
    """

    ids_prompts = []
    first = True
    for line in lines:
        line = line.strip().lower()

        # in a group, the first one is the KEY. 
        # all others are part of the set. 
        if len(line) == 0:
            first = True
        else:
            if first and line.startswith("prompt"):
                key, prompt = line.split(FIELDSEP)
                ids_prompts.append((key, prompt))
                first = False

    return ids_prompts


def strip_punctuation(text: str) -> str:
    """
    Remove punctuations of several languages, including Japanese.
    """
    return "".join(
        itertools.filterfalse(lambda x: unicodedata.category(x).startswith("P"), text)
    )


def read_transfile(lines: List[str], strip_punc=True, weighted=False) -> Dict[str, Dict[str, float]]:
    """
    This reads a file in the shared task format, and returns a dictionary with prompt IDs as 
    keys, and each key associated with a dictionary of responses. 
    """
    data = {}
    first = True
    options = {}
    key = ""
    for line in lines:
        line = line.strip().lower()

        # in a group, the first one is the KEY. 
        # all others are part of the set. 
        if len(line) == 0:
            first = True
            if len(key) > 0 and len(options) > 0:
                if key in data:
                    print("Warning: duplicate sentence! %s"%key)
                data[key] = options
                options= {}
        else:
            if first and line.startswith("prompt"):
                key, _ = line.strip().split(FIELDSEP)
                first = False
            else:
                # allow that a line may have a number at the end specifying the weight that this element should take. 
                # this is controlled by the weighted argument.
                # gold is REQUIRED to have this weight.
                if weighted:
                    # get text
                    text, weight = line.strip().split(FIELDSEP)
                else:
                    text = line.strip()
                    weight = 1

                if strip_punc:
                    text = strip_punctuation(text)

                options[text] = float(weight)

    # check if there is still an element at the end.
    if len(options) > 0:
        data[key] = options

    return data
