# idcode

idcode 是一个使用 Python 编写的命令行工具，用于交互式检测并解码编码文本。它支持命令行输入和文件输入，可以自动检测编码类型和尝试解码，并提供了一个交互式界面来逐步解码编码文本。

## 支持的编码格式

idcode 支持多种编码格式，包括：

- Base85/Base64/Base32
- Base94/Base92/Base91/Ascii85/AdobeAscii85/Z85/Base58/Base45/Base36/Base8
- Binary 编码
- Hex 编码
- URL 编码
- HTML 实体编码
- Quoted-printable 编码
- 核心价值观编码

## 安装

从 PyPi 安装：

```sh
pip install idcode
```

## 用法

idcode 支持交互式输入、命令行输入和文件输入来获取编码文本。

### 交互式输入

当不给出任何命令行参数时，程序会在运行后提示你给出目标文本：

```sh
idcode
```

### 命令行输入

要使用命令行输入方式来解码编码文本，你可以运行以下命令：

```sh
idcode -t "编码文本"
```

其中，`-t` 参数用于指定要解码的文本。

### 文件输入

要使用文件输入方式来解码编码文本，你可以运行以下命令：

```sh
idcode -f "文件路径"
```

其中，`-f` 参数用于指定包含编码文本的文件路径。

## 贡献

如果你发现了 bug，或者有改进建议，请随时创建 issue 或者 pull request。我们欢迎任何形式的贡献。

## 许可证

idcode 使用 MIT 许可证。请参阅 LICENSE 文件了解更多详情。