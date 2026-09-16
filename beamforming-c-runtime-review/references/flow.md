# 两麦 Beamforming C runtime 交接流程

这份参考用于和 DSP 工程师逐层对拍。主机 C runtime 的职责是复现算法
数据流；没有 Xtensa/NatureDSP 工具链时，不把它当作芯片 bit-exact 结果。

## 端到端数据流

```text
stereo int16 WAV
  -> planar80: mic0[80], mic1[80]
  -> 每通道 256 点历史缓冲
  -> Hann + 256 点 FFT
  -> 129 个非负频点的双麦快照 x[k]
  -> 空间协方差 EMA
  -> 对角加载 + 2x2 MVDR 权值
  -> y[k] = w[k]^T x[k]
  -> 可选 DSP mask
  -> 共轭补频 + 实数 iFFT
  -> OLA 输出 80 点 mono int16
```

## 各层应检查什么

1. 输入：确认 16 kHz、双声道、int16、左/右声道对应哪一个物理麦克风。
2. FFT：确认 256 点历史窗口、80 点 hop、Hann 表、FFT 缩放和频点顺序。
3. 协方差：确认 `R = E[x x^H]`、交叉谱虚部符号、EMA 初值和更新周期。
4. MVDR：确认对角加载、行列式奇异保护、导向矢量、无失真归一化，以及
   权值和输出的共轭约定必须成对一致。
5. 频域应用：确认复数乘加、公共 Q 对齐、129 个频点的边界处理。
6. iFFT/OLA：确认负频点镜像、DC/Nyquist 虚部清零、窗和 overlap-add 状态。
7. 后处理：先关闭 DRC；确认纯 MVDR 正常后再打开 mask，最后才评估电平处理。

## 建议的对拍顺序

对同一个 planar80 文件，按以下顺序保存中间量：

```text
FFT snapshot -> covariance -> MVDR weights -> weighted spectrum
             -> mask energy -> iFFT block -> OLA PCM
```

任一层首次出现明显差异，就先停在该层，不要用最终听感猜测根因。主机
测试通过只能说明 C runtime 自洽；最终 DSP 验收还需要目标工具链或芯片的
golden vector。

## 当前推荐模式

- `mvdr`：推荐的基础空间滤波路径。
- `dsp_mask`：在 MVDR 后增加现有规则 mask，需用真实数据试听确认。
- `dsp_mask_drc`：仅诊断 DRC 对电平的影响，当前不建议作为交付默认路径。
