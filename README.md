# Fluent-Toys

![image](https://github.com/Duke486/Fluent-Toys/blob/main/poster.jpg)

本仓库收录了中国矿业大学“程序设计综合实践”课程的开发项目，包含以下内容。项目界面基于 [@zhiyiYo](https://qfluentwidgets.com/) 的 **QFluentWidget** 库，采用 Fluent Design 风格，支持 Mica 材质效果和暗色模式，为用户提供了现代化的视觉体验。

## 项目列表

1. **简单计算器**  
   一个基于 `PyQt5` 和 `QFluentWidget` 开发的多功能计算器，支持以下功能：
   - 标准计算
   - 单位换算
   - 进制转换
   - AI 辅助的经济计算功能  

2. **拼图游戏**  
   支持从内置或自定义图片裁剪生成拼图，功能包括：
   - 多种难度选择：3x3、4x4、5x5
   - 快速查看原图
   - 一键通关  

3. **多文档文本编辑器**  
   支持多标签文本编辑功能，集成 AI 写作助手，可完成以下任务：
   - 续写，总结等
   - 聊天对话
   - 画布

---

## 运行方法

:::warning
您需要在ai.py、mtexteditor_interface.py中填写自己的OpenAI兼容API_KEY。在修改图像等资源时，请重新编译qrc文件。
:::

1. **要求**  
   - Python 版本：`3.8` 及以上  

2. **依赖安装**  
   在项目根目录下执行以下命令安装依赖：
   > `pip install -r requirements.txt`

3. **运行项目**  
   在命令行中进入项目目录并运行：
   > `python main.py`

---

## 使用 PyInstaller 打包为 exe

1. 使用以下命令进行安装：  
   > `pip install pyinstaller`

2. 项目根目录运行：  
   > `pyinstaller --noconfirm --onefile --windowed main.py`  

3. 打包完成后，可在 `dist` 文件夹中找到生成的 `main.exe` 文件。

---

## 项目特点

- **现代化界面设计**：全面采用 Fluent Design 风格，支持 Mica 材质效果与暗色模式。
- **模块化结构**：每个项目功能独立，主程序通过导航栏切换。
- **AI 支持**：文本编辑器和计算器内嵌 AI 功能，提升智能化体验。

---

欢迎贡献代码或提交 Issues！  
