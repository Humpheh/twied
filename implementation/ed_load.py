import pprint
import pickle
import argparse

parser = argparse.ArgumentParser(description="Load the event detection results")
parser.add_argument('input', help='the input file to load')
args = parser.parse_args()

pkl_file = open(args.input, 'rb')

data1 = pickle.load(pkl_file)
pprint.pprint(data1)
