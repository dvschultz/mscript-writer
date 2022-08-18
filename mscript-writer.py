import os
import subprocess
import shutil
import argparse
import cv2

class OpticalPrinter:
    def __init__(self, p1f, p2f, cf):
        self.p1f = p1f
        self.p2f = p2f
        self.cf = cf

def parse_args():
    desc = "write mscript scripts" 
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-o','--output', type=str,
        default='./output/output.txt',
        help='Directory path to the output.txt. (default: %(default)s)')

    parser.add_argument('-m','--mask_type', type=str,
        default='screen',
        help='masking between proj1 and proj2  (default: %(default)s)')

    parser.add_argument('-of','--output_folder', type=str,
        default='./output/',
        help='Directory path to the outputs folder. (default: %(default)s)')

    parser.add_argument('-ot','--onthe', type=int,
        default=2,
        help='How many frames one image should equal. (default: %(default)s)')

    parser.add_argument('-p1i','--proj1_input', type=str,
        default='./proj1_input/',
        help='path to proj1 frames. (default: %(default)s)')

    parser.add_argument('-p1s','--proj1_start', type=int,
        default=1,
        help='Frame to start proj1 video from. (default: %(default)s)')

    parser.add_argument('-p2i','--proj2_input', type=str,
        default='./proj2_input/',
        help='path to proj2 frames. (default: %(default)s)')

    parser.add_argument('-p2s','--proj2_start', type=int,
        default=1,
        help='Frame to start proj2 video from. (default: %(default)s)')

    parser.add_argument('--ffmpeg', dest='ffmpeg', action='store_true')

    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument('--supports_two_projector', dest='two_projector', action='store_true')
    feature_parser.add_argument('--single_proj', dest='two_projector', action='store_false')
    parser.set_defaults(two_projector=False)

    args = parser.parse_args()
    return args

def generate_video():
    input_folder = os.path.join(args.output_folder, "%09d.png")
    cmd=f'ffmpeg -y -r 24 -i {input_folder} -vcodec libx264 -pix_fmt yuv420p {args.output_folder}/video.mp4'
    subprocess.call(cmd, shell=True)

def get_matte(v):
    img_in_path_p1 = os.path.join(args.proj1_input,str(v.p1f).zfill(9) + '.png')
    img_in_path_p2 = os.path.join(args.proj2_input,str(v.p2f).zfill(9) + '.png')
    img_p1 = cv2.imread(img_in_path_p1)
    # print(img_p1.shape)
    p1_matte = cv2.cvtColor(img_p1,cv2.COLOR_BGR2GRAY)
    p1_matte_inv = cv2.bitwise_not(p1_matte)
    # cv2.imwrite(os.path.join(args.output_folder, 'test.png'), p1_matte)
    img_p2 = cv2.imread(img_in_path_p2)
    # print(img_p2.shape)

    return cv2.bitwise_and(img_p2,img_p2,mask = p1_matte)

def writecam():
    for x in range(args.onthe):
        text.append('\tCF')

def writeprojf():
    if(args.two_projector):
        text.append('\tP2F')
    else:
        text.append('\tPF #FIX IN SEQUENCER')

def oneoneloop_proj1(loop_count, v):
    print(v)
    text.append('LOOP ' + str(loop_count))
    writecam()
    text.append('\tPF')
    text.append('END LOOP')

    if(args.ffmpeg):
        for l in range(loop_count):
            img_in_path = os.path.join(args.proj1_input,str(v.p1f).zfill(9) + '.png')
            img_out_path = os.path.join(args.output_folder, str(v.cf).zfill(9) + '.png') 
            shutil.copy2(img_in_path, img_out_path)

            for o in range(args.onthe):
                img_in_path = os.path.join(args.proj1_input,str(v.p1f).zfill(9) + '.png')
                img_out_path = os.path.join(args.output_folder, str(v.cf).zfill(9) + '.png') 
                shutil.copy2(img_in_path, img_out_path)
                v.cf +=1

            v.p1f += 1

def oneoneloop_both(loop_count, v):
    text.append('LOOP ' + str(loop_count))
    writecam()
    text.append('\tP2F')
    text.append('\tPF')
    text.append('END LOOP')

    if(args.ffmpeg):
        for h in range(loop_count):
            matted = get_matte(v)
            img_out_path = os.path.join(args.output_folder, str(v.cf).zfill(9) + '.png') 
            cv2.imwrite(img_out_path, matted)
            v.p1f +=1
            v.p2f +=1
            v.cf +=1

def writehold_one(hold_count, v):
    text.append('#HOLD ' + str(hold_count) + ' \n')
    for h in range(hold_count):
        writecam()
    text.append('PF')
    text.append('\n')

    if(args.ffmpeg):
        img_in_path = os.path.join(args.proj1_input,str(v.p1f).zfill(9) + '.png')
        img_out_path = os.path.join(args.output_folder, str(v.cf).zfill(9) + '.png') 
        shutil.copy2(img_in_path, img_out_path)

        for l in range(hold_count):
            for o in range(args.onthe):
                img_in_path = os.path.join(args.proj1_input,str(v.p1f).zfill(9) + '.png')
                img_out_path = os.path.join(args.output_folder, str(v.cf).zfill(9) + '.png') 
                shutil.copy2(img_in_path, img_out_path)
                v.cf +=1

        v.p1f += 1

def writehold_two(hold_count, v):
    text.append('#HOLD ' + str(hold_count) + ' \n')
    for h in range(hold_count):
        writecam()
    text.append('P2F')
    text.append('\n')

    if(args.ffmpeg):
        img_in_path = os.path.join(args.proj2_input,str(v.p2f).zfill(9) + '.png')
        img_out_path = os.path.join(args.output_folder, str(v.cf).zfill(9) + '.png') 
        shutil.copy2(img_in_path, img_out_path)

        for l in range(hold_count):
            for o in range(args.onthe):
                img_in_path = os.path.join(args.proj2_input,str(v.p2f).zfill(9) + '.png')
                img_out_path = os.path.join(args.output_folder, str(v.cf).zfill(9) + '.png') 
                shutil.copy2(img_in_path, img_out_path)
                v.cf +=1

        v.p2f += 1

#animate projector 2 while holding projector 1
def writetwo_holdone(hold_count, v):
    text.append('#HOLD ' + str(hold_count) + ' \n')
    for h in range(hold_count):
        writecam()
        text.append('P2F')

    text.append('PF')
    text.append('\n')

    if(args.ffmpeg):
        for h in range(hold_count):
            matted = get_matte(v)
            img_out_path = os.path.join(args.output_folder, str(v.cf).zfill(9) + '.png') 
            cv2.imwrite(img_out_path, matted)
            v.p2f +=1
            v.cf +=1

        v.p1f +=1


def writehold_both(hold_count, v):
    text.append('#HOLD ' + str(hold_count) + ' \n')
    for h in range(hold_count):
        text.append('CF')

    writeprojf()
    text.append('\n')

    if(args.ffmpeg):
        matted = get_matte(v)
        
        for h in range(hold_count):
            img_out_path = os.path.join(args.output_folder, str(v.cf).zfill(9) + '.png') 
            cv2.imwrite(img_out_path, matted)
            v.cf +=1

def main():
    global args, text, p1f, p2f, cf
    args = parse_args()

    if not os.path.exists(args.output_folder): os.makedirs(args.output_folder)

    text = []
    p1f = int(args.proj1_start)
    p2f = int(args.proj2_start)
    cf = 0

    v = OpticalPrinter(p1f, p2f, cf)
    
    start_count = 24
    decay = 2

    while start_count > 1:
        count = start_count
        while count > 0:
            # writehold_one(count, v)
            # writehold_two(count, v)
            writetwo_holdone(count, v)
            count = int(count/decay)

        start_count = int(start_count/decay)

    # oneoneloop_proj1(24, v)

    oneoneloop_both(72, v)

    # writehold_both(24, v)

    generate_video()
    


    with open(args.output, 'w') as f:
        f.write("\n".join(text))

if __name__ == "__main__":
    main()

