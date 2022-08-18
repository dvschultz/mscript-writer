import os
import argparse
import numpy as np

def parse_args():
    desc = "Tools to normalize an image dataset" 
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-o','--output', type=str,
        default='./output/output.txt',
        help='Directory path to the outputs folder. (default: %(default)s)')

    parser.add_argument('-t','--txt', type=str,
        default='./input/colors.npz',
        help='Directory path to the npz file. (default: %(default)s)')

    parser.add_argument('-max','--max', type=int,
        default=24,
        help='How many frames to produce. (default: %(default)s)')

    parser.add_argument('-min','--min', type=int,
        default=1,
        help='How many frames to produce. (default: %(default)s)')

    parser.add_argument('--invert', dest='invert', action='store_true')
    parser.set_defaults(invert=False)

    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument('--supports_two_projector', dest='two_projector', action='store_true')
    feature_parser.add_argument('--single_proj', dest='two_projector', action='store_false')
    parser.set_defaults(two_projector=True)

    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument('--film', dest='matte', action='store_false')
    feature_parser.add_argument('--matte', dest='matte', action='store_true')
    parser.set_defaults(matte=False)

    args = parser.parse_args()
    return args

def map(x,imin,imax,omin,omax):
	return int(omin + (omax - omin) * ((x - imin) / (imax - imin)))

def writehold_one(hold_count):
    text.append('#HOLD ' + str(hold_count) + ' \n')
    for h in range(hold_count):
        text.append('CF')

    text.append('PF')
    text.append('\n')

def writeone_holdtwo(hold_count):
    text.append('#HOLD PROJ TWO ' + str(hold_count) + ' \n')
    for h in range(hold_count):
        text.append('CF')
        text.append('PF')

    writeprojf()
    text.append('\n')

def writetwo_holdone(hold_count):
    text.append('#HOLD PROJ ONE ' + str(hold_count) + ' \n')
    for h in range(hold_count):
        text.append('CF')
        text.append('P2F')

    text.append('PF')
    text.append('\n')

def writeprojf():
    if(args.two_projector):
        text.append('P2F')
    else:
        text.append('PF')
        text.append('#FIX IN SEQUENCER')

def main():
	global args, text, numbers
	args = parse_args()

	file = open(args.txt, 'r')
	lines = file.readlines()

	numbers = []
	for line in lines:
		numbers.append(float(line.strip().replace(',','')))
	
	diffs = []
	for i in range(len(numbers)):
		if(i < len(numbers)-1):
			diffs.append([np.abs(numbers[i+1] - numbers[i])])

	diff_array = np.array(diffs)
	print(numbers)
	print(diffs)

	max = diffs[np.argmax(diff_array)][0]
	min = diffs[np.argmin(diff_array)][0]
	# print(diffs[np.argmax(diff_array)])

	print(max, min)
	print(diffs[0])


	steps = []
	for d in diffs:
		if(args.invert):
			steps.append(map(d[0],float(min),float(max),float(args.max),float(args.min)))
		else:
			steps.append(map(d[0],float(min),float(max),float(args.min),float(args.max)))

	print(steps)

	text = []

	for s in steps:
		if(args.matte):
			# writeone_holdtwo(s)
			writetwo_holdone(s)
		else:
			writehold_one(s)

	with open(args.output, 'w') as f:
		f.write("\n".join(text))


if __name__ == "__main__":
    main()