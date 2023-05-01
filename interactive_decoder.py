class InteractiveDecoder:
    def __init__(self, encodings, encoded_text):
        self.encodings = encodings
        self.initial_state = {'text': encoded_text, 'steps': []}
        self.states = [self.initial_state]

    def display_results(self, detected_encodings, successful_results):
        if detected_encodings:
            print("检测到的编码（自动解码失败）：")
            for encoding in detected_encodings:
                print(f" - {encoding.__name__}")
            print("\n可能的解码结果：")

        for i, (decoded_text, encoding_used) in enumerate(successful_results):
            print(f"{i + 1}. 编码算法：{encoding_used}\n解码后的文本：\n{decoded_text}\n" + "-" * 40)

    def process_choice(self, choice, successful_results):
        if choice == -1:
            if len(self.states) > 1:
                self.states.pop()  # Remove the current state and go back to the previous one.
            else:
                print("已经是初始状态，无法回退。")
        else:
            chosen_result = successful_results[choice - 1]
            new_text = chosen_result[0]
            new_step = chosen_result[1]
            new_steps = self.states[-1]['steps'] + [new_step]
            new_state = {'text': new_text, 'steps': new_steps}
            self.states.append(new_state)

    def run(self):
        while True:
            current_state = self.states[-1]
            current_text = current_state['text']
            successful_results = []
            detected_encodings = []

            for encoding in self.encodings:
                if encoding.is_valid(current_text):
                    success, decoded_text = encoding.try_decode(current_text)
                    if success:
                        successful_results.append((decoded_text, encoding.__name__))
                    else:
                        detected_encodings.append(encoding)

            if not successful_results and not detected_encodings:
                print("无法继续解码。")
                break

            self.display_results(detected_encodings, successful_results)

            print("选择一个结果进行下一步解码，输入0退出解码，输入-1回退到上一步。")
            choice = int(input("输入你的选择："))

            if choice == 0:
                break

            self.process_choice(choice, successful_results)

        return current_state['text'], current_state['steps']
