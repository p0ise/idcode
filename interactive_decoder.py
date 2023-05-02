from preprocessing import remove_prefixes, remove_separators, unify_case


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

    def display_menu(self, menu_options):
        for i, option in enumerate(menu_options, start=1):
            print(f"{i}. {option}")

        choice = int(input("输入你的选择："))
        return choice

    def preprocess_menu(self):
        while True:
            current_state = self.states[-1]
            current_text = current_state['text']

            print(self.color_text("\n选择预处理操作：", 94))
            menu_options = [
                "去除前缀",
                "去除分隔符",
                "统一大小写",
                "返回主菜单"
            ]
            choice = self.display_menu(menu_options)

            if choice == len(menu_options):
                break

            operation = menu_options[choice - 1]

            if operation == "去除前缀":
                new_text = remove_prefixes(current_text)
            elif operation == "去除分隔符":
                new_text = remove_separators(current_text)
            elif operation == "统一大小写":
                new_text = unify_case(current_text)
            else:
                print(self.color_text("无效的输入，请重新输入。", 91))
                continue

            if new_text == current_text:
                print(self.color_text("无需进行该操作。", 93))
            else:
                new_steps = self.states[-1]['steps'] + [operation]
                new_state = {'text': new_text, 'steps': new_steps}
                self.states.append(new_state)

                print(self.color_text("\n预处理后的密文：", 96))
                print(new_text)

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

    def decode_menu(self):
        while True:
            current_state = self.states[-1]
            current_text = current_state['text']

            detected_encodings, successful_results = self.detect_and_decode(
                current_text)

            if not successful_results and not detected_encodings:
                print(self.color_text("无法继续解码。", 93))
                break

            if detected_encodings:
                print(self.color_text("检测到的编码（自动解码失败）：", 93))
                for encoding in detected_encodings:
                    print(f" - {encoding}")

            print(self.color_text("\n成功解码的结果：", 92))
            if successful_results:
                for i, (decoded_text, encoding_used) in enumerate(successful_results):
                    print(
                        f"{i + 1}. 编码算法：{encoding_used}\n解码后的文本：\n{decoded_text}\n" + "-" * 40)
            else:
                print("无")

            print(self.color_text("选择一个结果进行下一步解码，输入0退出解码，输入-1回退到上一步。", 94))
            choice = int(input("输入你的选择："))

            if choice == 0:
                break

            if choice == -1:
                self.go_back()
            else:
                chosen_result = successful_results[choice - 1]
                new_text = chosen_result[0]
                new_step = chosen_result[1]
                new_steps = self.states[-1]['steps'] + [new_step]
                new_state = {'text': new_text, 'steps': new_steps}
                self.states.append(new_state)
                current_text = new_text

    def main_menu(self):
        while True:
            current_state = self.states[-1]
            current_text = current_state['text']

            print(self.color_text("\n当前密文：", 96))
            print(current_text)
            print(self.color_text("\n选择一个操作：", 94))
            menu_options = [
                "预处理密文",
                "检测编码并尝试解码",
                "返回上一步",
                "退出"
            ]
            choice = self.display_menu(menu_options)

            if choice == 1:
                self.preprocess_menu()
            elif choice == 2:
                self.decode_menu()
            elif choice == 3:
                self.go_back()
            elif choice == 4:
                break
            else:
                print(self.color_text("无效的输入，请重新输入。", 91))

    def run(self):
        self.main_menu()
        final_state = self.states[-1]
        return final_state['text'], final_state['steps']
