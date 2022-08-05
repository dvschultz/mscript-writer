import os
import argparse

def parse_args():
    desc = "write mscript scripts" 
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-o','--output', type=str,
        default='./output/output.txt',
        help='Directory path to the outputs folder. (default: %(default)s)')

    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument('--supports_two_projector', dest='two_projector', action='store_true')
    feature_parser.add_argument('--single_proj', dest='two_projector', action='store_false')
    parser.set_defaults(two_projector=False)

    args = parser.parse_args()
    return args

def oneoneloop_proj1(loop_count):
    text.append('LOOP ' + str(loop_count))
    text.append('\tCF')
    text.append('\tPF')
    text.append('END LOOP')

def oneoneloop_both(loop_count):
    text.append('LOOP ' + str(loop_count))
    text.append('\tCF')
    writeprojf()
    text.append('END LOOP')

def writehold_one(hold_count):
    text.append('#HOLD ' + str(hold_count) + ' \n')
    for h in range(hold_count):
        text.append('CF')

    text.append('\tPF')
    text.append('\n')

def writehold_both(hold_count):
    text.append('#HOLD ' + str(hold_count) + ' \n')
    for h in range(hold_count):
        text.append('CF')

    writeprojf()
    text.append('\n')

def writeprojf():
    if(args.two_projector):
        text.append('\tP2F')
    else:
        text.append('\tPF #FIX IN SEQUENCER')

def main():
    global args, text
    args = parse_args()

    text = []

    start_count = 24
    decay = 2
    
    while start_count > 1:
        count = start_count
        while count > 0:
            writehold_one(count)
            count = int(count/decay)

        start_count = int(start_count/decay)

    oneoneloop_proj1(24)

    oneoneloop_both(24)
    


    with open(args.output, 'w') as f:
        f.write("\n".join(text))

if __name__ == "__main__":
    main()

