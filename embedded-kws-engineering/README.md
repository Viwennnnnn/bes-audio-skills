# Embedded KWS Engineering Skill

用于嵌入式关键词唤醒项目的数据审计、流式模型训练评估、阈值选取、M 类 MCU 部署对齐、串口自动化回归和失败样本诊断。

## 使用

将整个 `embedded-kws-engineering` 目录复制到 Codex Skills 目录，然后在任务中使用：

```text
$embedded-kws-engineering 审计这套 KWS 数据，并检查 train/dev/test 泄漏。
```

Codex 也可以根据 `SKILL.md` 的描述自动选择该 Skill。

## 内容

- `SKILL.md`：入口、路由和不可破坏的实验规则。
- `references/`：数据、训练、真机回归、故障定位和工程整理方法。
- `scripts/`：不依赖第三方 Python 包的清单审计、结果统计和失败复测集生成工具。
- `agents/openai.yaml`：Codex 界面元数据。

脚本使用前先运行 `python scripts/<脚本名>.py --help`。不同项目字段不一致时，应显式适配脚本，不能猜测字段语义。

本仓库不包含训练语音、模型权重、服务器凭据、个人绝对路径或固件私有文件。
