#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import argparse
from interactive_decoder import InteractiveDecoder
from custom_encoding import all_encodings


def read_encoded_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def parse_arguments():
    parser = argparse.ArgumentParser(description="解码器：支持命令行输入和文件输入")
    parser.add_argument('-f', '--file', type=str, help="包含密文的文件路径")
    parser.add_argument('-t', '--text', type=str, help="直接输入密文")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()

    if args.file and not os.path.exists(args.file):
        print(f"文件 '{args.file}' 不存在。")
        exit(1)

    if not args.file and not args.text:
        print("请使用-f/--file 或者 -t/--text 参数提供密文。")
        exit(1)

    if args.file:
        encoded_text = read_encoded_text_from_file(args.file)
    elif args.text:
        encoded_text = args.text
    else:
        print("请使用-f/--file 或者 -t/--text 参数提供密文。")
        exit(1)

    decoder = InteractiveDecoder(all_encodings, encoded_text)

    decoded_text, steps = decoder.run()

    print("\n最终解码结果：")
    print(decoded_text)
    print("\n经过的解码方式：")
    print(" -> ".join(steps))
