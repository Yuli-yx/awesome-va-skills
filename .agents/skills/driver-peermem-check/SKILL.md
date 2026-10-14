---
name: driver-peermem-check
description: |
  分析 Ascend 驱动 .run 包中是否包含 npu_peermem.ko 及相关源码。适用于：
  - 判断某个驱动版本是否支持 d2d/d2rd RDMA 传输
  - 对比不同平台的驱动包内容差异
  - 检查 npu_peermem 模块的构建依赖是否就绪
  - 用户提到驱动包、npu_peermem、d2d RDMA 失败、peer memory 等问题时
license: CANN Open Software License Agreement Version 2.0
---

# 驱动包 npu_peermem 检查

分析 Ascend 驱动 .run 包，判断是否包含 `npu_peermem.ko` 内核模块及相关源码。

## 分析流程

### 1. 获取驱动包基本信息

```bash
ls -lh <driver.run>        # 文件大小
file <driver.run>          # 确认是 makeself 自解压包
```

文件名格式：`Atlas-A5-hdk-npu-driver_<version>_linux-<arch>.run`
- `<version>`：驱动版本号（如 25.6.rc1.b121）
- `<arch>`：目标平台（x86-64 或 aarch64）

### 2. 无需 root 提取驱动包内容

```bash
# 方法一（推荐）：--noexec 仅解压不执行安装脚本
bash <driver.run> --noexec --target <extract_dir>

# 方法二：直接跳过 makeself 头部提取 tar 包体
tail -n +720 <driver.run> | tar -xz -C <extract_dir>
```

### 3. 使用检查脚本

运行 `scripts/check_npu_peermem.sh <extract_dir> [package_name]`，脚本会执行以下检查：

| 检查项 | 文件/位置 | 说明 |
|--------|-----------|------|
| **内核模块文件** | `driver/host/npu_peermem.ko` | 已编译的 .ko 文件是否存在 |
| **源码目录** | `driver/kernel/ndr/npu_peermem.c` | 核心源码是否存在 |
| **头文件** | `driver/kernel/ndr/peer_mem.h` | IB peer memory 接口头文件 |
| **Makefile** | `driver/kernel/ndr/Makefile` | 构建系统是否包含 ndr 模块 |
| **构建脚本引用** | `driver/script/deal_ko.sh` | deal_ko.sh 中对 npu_peermem 的处理（含排除逻辑） |
| **热复位脚本引用** | `driver/script/device_hot_reset.sh` | 热复位脚本中是否有防御性检查 |
| **模块列表** | `driver/script/specific_func.inc` | 标准模块列表中是否包含 |
| **CMake 构建** | `driver/kernel/ndr/CMakeLists.txt` | CMake 备用构建文件 |

### 4. 分析构建依赖（仅有源码时）

如果存在源码（`driver/kernel/ndr/`），进一步分析编译条件：

```bash
# 查看 Makefile 中需要的环境变量
grep -E '(HIAI_DKMS_DIR|OFA_SYMVERS_DIR|IB_PEER_MEM)' <extract_dir>/driver/kernel/ndr/Makefile

# 查看 OFED 符号检测脚本
cat <extract_dir>/driver/kernel/ndr/find_ofed_symvers.sh
```

编译该模块需要三个条件：
- **Ascend DKMS**：`HIAI_DKMS_DIR` 指向 Ascend 驱动源码根目录
- **OFED/RDMA**：`OFA_SYMVERS_DIR` 指向含 `ib_register_peer_memory_client` 符号的 `Module.symvers`
- **内核构建环境**：标准 kernel-devel / kernel-headers

### 5. 输出结论

固定输出格式：

- **模块是否存在**：是 / 否
- **源码是否存在**：是 / 否
- **版本**：从文件名提取
- **平台**：x86-64 / aarch64
- **可能原因**（若缺失）：新版移除 / 合并到其他 ko / 构建时缺少 OFED / 架构不支持
- **影响**：无此模块时 d2d / d2rd RDMA 传输将失败，h2h 不受影响
