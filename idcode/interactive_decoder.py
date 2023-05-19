class InteractiveDecoder:
    def __init__(self, encodings, encoded_text):
        self.encodings = encodings
        self.initial_state = {'text': encoded_text, 'steps': []}
        self.states = [self.initial_state]

    def go_back(self):
        if len(self.states) > 1:
            # Remove the current state and go back to the previous one.
            self.states.pop()
        else:
            print(self.color_text("已经是初始状态，无法回退。", 91))

    def color_text(self, text, color_code):
        return f"\033[{color_code}m{text}\033[0m"

    def detect_and_decode(self, current_text):
        successful_results = []
        detected_encodings = []

        for encoding in self.encodings:
            if encoding.is_valid(current_text):
                success, decoded_text = encoding.try_decode(current_text)
                if success:
                    successful_results.append(
                        (decoded_text, encoding.__name__))
                else:
                    detected_encodings.append(encoding.__name__)

        return detected_encodings, successful_results

    def main_menu(self):
        while True:
            current_state = self.states[-1]
            current_text = current_state['text']

            print(self.color_text("当前密文：", 96))
            print(current_text)
            print()

            detected_encodings, successful_results = self.detect_and_decode(
                current_text)

            if not successful_results and not detected_encodings:
                print(self.color_text("无法继续解码。", 93))
                break

            if detected_encodings:
                print(self.color_text("检测到的编码（自动解码失败）：", 93))
                for encoding in detected_encodings:
                    print(f" - {encoding}")
                print()

            print(self.color_text("成功解码的结果：", 92))
            if successful_results:
                for i, (decoded_text, encoding_used) in enumerate(successful_results):
                    print(
                        f"{i + 1}. 编码算法：{encoding_used}\n解码后的文本：\n{decoded_text}\n" + "-" * 40)
            else:
                print("无")

            print(self.color_text("选择一个结果进行下一步解码，输入0退出解码，输入-1回退到上一步。", 94))
            choice = int(input("输入你的选择："))
            print()

            if choice == 0:
                break

            if choice == -1:
                self.go_back()
            else:
                chosen_result = successful_results[choice - 1]
                new_text, new_step = chosen_result
                new_steps = self.states[-1]['steps'] + [new_step]
                new_state = {'text': new_text, 'steps': new_steps}
                self.states.append(new_state)

    def run(self):
        self.main_menu()

        final_state = self.states[-1]

        print(self.color_text("最终解码结果：", 92))
        print(final_state['text'])
        print(self.color_text("经过的解码方式：", 92))
        print(" -> ".join(final_state['steps']))
