#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import argparse
from .interactive_decoder import InteractiveDecoder
from .custom_encoding import all_encodings


def read_encoded_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def parse_arguments():
    parser = argparse.ArgumentParser(description="解码器：支持命令行输入和文件输入")
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('-f', '--file', type=str, help="包含密文的文件路径")
    input_group.add_argument('-t', '--text', type=str, help="直接输入密文")

    return parser.parse_args()


def get_encoded_text(args):
    if args.file:
        if not os.path.exists(args.file):
            print(f"文件 '{args.file}' 不存在。")
            exit(1)
        return read_encoded_text_from_file(args.file)
    elif args.text:
        return args.text
    else:
        while True:
            encoded_text = input("请输入密文：\n")
            if encoded_text:
                return encoded_text
            else:
                print("密文不能为空，请重新输入。")


def main():
    args = parse_arguments()

    encoded_text = get_encoded_text(args)

    decoder = InteractiveDecoder(all_encodings, encoded_text)

    decoder.run()


if __name__ == '__main__':
    main()
