#!/usr/bin/python

import os
import subprocess
import argparse

class Statics:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
  
def gpg_encrypt_file(src_file, dst_file, keyid):
    ret = subprocess.call(["gpg", "--encrypt", "-r", keyid,
                           "--trust-model", "always",
                           "-o", dst_file, src_file])
    return ret == 0

def gpg_decrypt_file(src_file, dst_file, keyid):
    ret = subprocess.call(["gpg", "--decrypt", "-r", keyid,
                           "--trust-model", "always",
                           "-o", dst_file, src_file])
    return ret == 0

def gpg_dir(src_dir, dst_dir, keyid, decrypt, stat):
    for dirpath, _, filenames in os.walk(src_dir):
        for src_fname in filenames:
            if decrypt and not src_fname.endswith(".gpg"):
                continue
            src_file = os.path.join(dirpath, src_fname)
            rel_dir = os.path.relpath(dirpath, src_dir)
            dst_file_dir = os.path.join(dst_dir, rel_dir)
            if decrypt:
                dst_file = os.path.join(dst_file_dir, src_fname[0:-4])
            else:
                dst_file = os.path.join(dst_file_dir, src_fname + ".gpg")
            print("%s -> %s" % (src_file, dst_file))
            if not os.path.exists(dst_file_dir):
                os.makedirs(dst_file_dir)
            if decrypt:
                success = gpg_decrypt_file(src_file, dst_file, keyid)
            else:
                success = gpg_encrypt_file(src_file, dst_file, keyid)
            stat.total += 1
            if success:
              stat.success += 1
            else:
              stat.failed += 1

def main():
    parser = argparse.ArgumentParser(description="encrypt/decrypt directory with gpg")
    parser.add_argument("-d" , "--decrypt",
                        help = "decrypt instead encrypt",
                        action = "store_true",
                        dest = "decrypt")
    parser.add_argument("-r" , "--recipient",
                        required = True,
                        help = "gpg user/key id",
                        dest = "recipient")
    parser.add_argument("src_dir",
                        help = "source directory to be processed")
    parser.add_argument("dst_dir",
                        help = "destination directory used to store result")
    args = parser.parse_args()
    #print("%s %s %s" % (args.recipient, args.src_dir, args.dst_dir))
    if not os.path.isdir(args.src_dir):
      print("'%s' is not directory" % args.src_dir)
      return
    if os.path.exists(args.dst_dir):
      print("directory '%s' already exists" % args.dst_dir)
      return
    stat = Statics()
    gpg_dir(args.src_dir, args.dst_dir, args.recipient, args.decrypt, stat)
    print("there are %d files, %d successed, %d failed"
          % (stat.total, stat.success, stat.failed))

if __name__ == '__main__':
    main()
