---
name: hccl-auto-test
description: >-
  在昇腾 A5 机器上安装 CANN 依赖、编译 hccl_test 算子并执行单机或跨机 HCCL 打流。
  覆盖裸机与容器、mpirun/mpich 安装、CCU/AIV/AICPU 三条验收命令、hostfile 与免密前置，
  以及打流失败后的日志定位（eid、tls、jfc、卡被占用、CANN 版本、逐机逐卡缩小范围）。
  用户提到 hccl_test、HCCL 打流、all_reduce_test、all_gather_test、alltoall_test、
  ccu_ms、aiv、aicpu_ts、hccl_rootinfo、vLLM 容器打流、卡被占用、A5 集合通信验收、
  全量性能测试、alltoallv、reduce_scatter、broadcast_test 时使用本 skill，
  即使用户只说「打流」或「环境验收集通信」。
---

# A5 HCCL 打流

在用户指定的 A5 机器上完成 hccl_test 环境准备并打流。

- **环境可用验收**（默认）：第 5 / 6 节 **CCU + AIV + AICPU 三条**，全部 `check_result` 为 `success` 才判定环境可用。
- **全量性能测试**（用户明确要求时）：第 7 节 **7 类算子 × AIV / AICPU 共 14 条**，用于性能数据归档，**不替代**三条验收结论。

**打流必须用当次在本机新编译并 `cp` 到 `mpich/bin` 的算子**（第 4 节）。`/home/tools/mpich/bin` 里残留的旧 `all_*_test` 会干扰验收，不能把「文件已存在」当成可打流。

打流失败时按「故障定位」处理。只使用那里列出的检查和修复，不要另编排查步骤。

修改本 skill 时，三处一起改，内容保持一致：

- Cursor：`/home/w00933270/.cursor/skills/hccl-auto-test/SKILL.md`
- Claude：`/home/w00933270/.claude/skills/hccl-auto-test/SKILL.md`
- 仓库 `personal_skills` 分支：`personal_skills/hccl-auto-test/SKILL.md`

仓库改完后提交并推到 `origin/personal_skills`，供其他人使用。不要推到 upstream。

## 执行前必须确认

未确认前不要安装、编译、改防火墙、写 `/etc`、关闭 TLS、重启或发起 mpirun。

1. 组网场景：先问用户本次是不是 1825 组网。是 1825 才需要 `/etc/hccl_rootinfo.json`，要生成并挂载；不是则不要使用或挂载它，挂了反而可能导致打流报错。**裸机打流同样适用**：非 1825 时打流前在 hostfile 涉及的每台机器上检查 `/etc/hccl_rootinfo.json` 是否仍存在；若存在，在用户同意下先 `mv` 为备份（例如 `/etc/hccl_rootinfo.json.bak`），再打流。误留过期或与现网不符的 rootinfo 会导致单机 `hccl_test_common.cc:901 retcode:4`、`DeserializeLevelList`、`DetectRankTable` 等，**不是** 1825 缺文件时的 eid 问题，也不要因此去生成新 rootinfo。
2. 打流位置：裸机，或容器。
3. 目标：哪台机器、是否已有 shell。跨机时列出全部物理机 IP。
4. CANN 安装路径。用户未另行指定时，默认 `/usr/local/Ascend/cann`。用户装在其他目录时，必须先拿到该路径再替换下文命令里的 CANN 相关路径。
5. 规模：单机 8 卡，指定卡，或跨机。跨机需要 hostfile 和每台机器的卡数。
6. mpich 压缩包是否已放到 `/home/tools/`。未提供压缩包时不要自己下载。
7. **打流目标**：仅 **环境可用验收**（三条），还是 **全量性能测试**（第 7 节）。全量测试前仍建议先完成三条验收；全量时向用户确认**报告输出目录**（发起机可写路径，见第 7 节，默认生成 **Markdown** 报告）。

改防火墙、在多台机器安装软件、拉起容器、写入 `/etc`、关闭 TLS 或重启，都要针对具体目标再取得一次明确同意。

## 路径约定

编译使用 `ascend-toolkit`，打流 `source` 使用 `cann/set_env.sh` 与 driver 的 `setenv.bash`。两套路径都保留，不要合并成一条。

环境变量在同一个 shell 窗口里只设置一遍。编译和后续打流都沿用这个窗口，不要为每条 mpirun 再开窗口或再 export 一遍。

下文命令使用用户给出的默认路径。CANN 不在默认位置时，先替换再执行。

| 用途 | 默认路径 |
| --- | --- |
| CANN 安装根目录 | `/usr/local/Ascend/cann` |
| 编译期 toolkit | `/usr/local/Ascend/ascend-toolkit` |
| toolkit latest | `/usr/local/Ascend/ascend-toolkit/latest` |
| 驱动环境 | `/usr/local/Ascend/driver/bin/setenv.bash` |
| HCCL topo | `/usr/local/Ascend/driver/topo/950/atlas_850_1.json` |
| mpich 前缀 | `/home/tools/mpich` |
| mpich 源码 | `/home/tools/mpich-3.2.1` |
| hostfile | `/home/tools/hostfile` |
| plog（裸机打流） | `/home/hccl_test/logs/plog` |
| plog（vLLM 容器拉起） | `/home/hccl_test/logs_pd` |

## 1. 裸机或容器

先向用户确认本次在裸机打流还是容器里打流。

mpirun 装在裸机上，不装进容器。容器通过挂载使用裸机上的 `/home/tools/mpich`。

`/home/tools/mpich/bin/mpirun` 已存在时跳过 **第 2 节** mpich 安装。**算子不能**仅凭本机 `/home/tools/mpich/bin` 里已有三个测试二进制就跳过 **第 4 节**：那些文件常是从别机拷来的旧产物。须在**每一台参与打流的物理机本机**按第 4 节 `make` 并 `cp` 到本机 `mpich/bin` 后，再打流（跨机时 hostfile 里每台都要各自编译一遍）。

容器里的 HCCL 打流执行的是第 5 节那三条 `mpirun`，不是下面的 `vllm serve`。`vllm serve` 会加载模型并占卡，占卡后不能打流。

容器跨机时，部分物理机可以不装 CANN。hostfile 仍填物理机 IP。每台机器起同一个镜像、同一个容器名。免密是宿主机 root 登录其他宿主机，不是容器里再登一次。`mpirun` 在发起机的宿主机上执行，远端进程通过各机相同的入口脚本 `docker exec` 进本机容器。

单机容器打流至少包括：

- `--privileged --network host`。`--network host` 是硬要求，不要改成独立 IP 的网络（bridge、macvlan 都不行）
- 设备：`/dev/davinci_manager`、本次要测的 `/dev/davinciN`、`/dev/hisi_hdc`。8 卡就是 `davinci0` 到 `davinci7`
- 挂载：驱动目录（默认 `/usr/local/Ascend/driver`）、`/home`
- `/dev/ummu`、`/dev/uburma` 在宿主机上是目录不是字符设备，用 `-v` 挂；写进 `--device` 会因不是字符设备而直接起不来
- `/etc/hccl_rootinfo.json`：1825 组网必须挂，文件不存在时按「故障定位 → eid 匹配不上」生成；其余组网不要挂，非 1825 挂了反而可能导致打流报错

`--network host` 不是图省事。A5 的 HCCL 数据面走 UB，容器里能看到 `ipourma0` 到 `ipourma9` 这 10 个接口，它们只存在于宿主机的网络命名空间。换成 bridge 等独立 IP 的网络，容器里只剩 `eth0` 和 `lo`，UB 接口一个都不剩，跨机打流无从谈起；容器自己那个地址（`172.17.0.0/16`）只挂在宿主 `docker0` 上，对端物理机根本路由不到。容器与宿主机共用 IP 是正常结果——物理 UB 链路只有一条，容器隔离的是 CANN 库和进程，不是物理链路。

镜像里已有 `ascend-toolkit` 和 `cann` 时，沿用镜像内这两套路径，只把宿主机驱动目录挂进去。环境变量用第 3 节，不要套用 vLLM 拉起命令里的 `ASCEND_RT_VISIBLE_DEVICES=0`。未指定镜像时用本机已有的 `vllm-ascend` 镜像，不要自己拉新镜像。打流容器跑完就删除。

拉起容器前仍需用户对具体目标明确同意。

下面是 vLLM 服务拉起命令，只用于起推理服务。挂载加在容器启动参数上，不要写进 `vllm serve`。`VLLM_VERSION` 只在需要特定 vLLM 版本时设置，否则不配。`nic_name` 和 `local_ip` 用 `ip -4 addr` 对照本机业务 IP 找到网卡后再改。样例中的 `eth2`、`192.0.2.102`、权重路径、端口和 `ASCEND_RT_VISIBLE_DEVICES=0` 对应该次单卡拉起。

```bash
# 需要特定版本vllm则配，否则不配
export VLLM_VERSION=0.21.0

export OMP_PROC_BIND=false
export OMP_NUM_THREADS=10

# 打开plog日志存入指定目录，便于之后的调试
export ASCEND_SLOG_PRINT_TO_STDOUT=0
export ASCEND_PROCESS_LOG_PATH=/home/hccl_test/logs_pd
export ASCEND_GLOBAL_LOG_LEVEL=1

export ASCEND_HOST_LOG_FILE_NUM=1000
export PYTORCH_NPU_ALLOC_CONF=expandable_segments:True
export HCCL_BUFFSIZE=1024
export ASCEND_RT_VISIBLE_DEVICES=0

# 使用UBOE链路传输
export ASCEND_GLOBAL_RESOURCE_CONFIG='{"comm_resource_config.protocol_desc":["uboe:device"]}'

rm -rf /home/hccl_test/logs_pd

#声明本机ip及其使用的网卡，加速通信过程 （使用ifconfig | grep -C5 {IP字段} 查看本机信息，然后按需修改）
nic_name="eth2"
local_ip="192.0.2.102"
export HCCL_IF_IP=$local_ip
export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=$nic_name

vllm serve /mnt/share/weight/Qwen3-30B-A3B-Instruct-2507 \
--served-model-name ds \
--trust-remote-code \
--max-num-seqs 24 \
--tensor-parallel-size 1 \
--data-parallel-size 1 \
--data-parallel-size-local 1 \
--port 30099 \
--max_model_len 30000 \
--max-num-batched-tokens 256 \
--enforce-eager \
--profiler-config '{"profiler": "torch", "torch_profiler_dir": "./vllm_profile", "torch_profiler_with_stack": false}' \
--no-enable-prefix-caching \
--gpu-memory-utilization 0.9 \
--async-scheduling \
--additional-config='{"enable_cpu_binding":false}' \
--kv-transfer-config '{"kv_connector": "MooncakeConnectorV1", "kv_role": "kv_producer", "kv_port": "20400", "engine_id": "2",
"kv_connector_extra_config": {
"prefill": {
"dp_size": 1,
"tp_size": 1
},
"decode": {
"dp_size": 1,
"tp_size": 1
}
}
}'
```

这条 vLLM 命令的 plog 目录是 `/home/hccl_test/logs_pd`。HCCL 打流用第 3 节的 `ASCEND_PROCESS_LOG_PATH`。后续 `grep` 用实际设置的目录。

## 2. 安装 mpirun

环境需要 mpirun，一般装在裸机。用户提供压缩包，agent 负责安装。压缩包上传到 `/home/tools/`。

```bash
tar -zxvf mpich-3.2.1.tar.gz
cd /home/tools/mpich-3.2.1
./configure --prefix=/home/tools/mpich --disable-fortran
make -j$(nproc) && make install
```

`/home/tools/mpich/bin/mpirun` 存在后跳过本步。压缩包不在、但 `mpirun` 已存在时，同样跳过，不要自己下载。

## 3. 同一窗口设置环境

在即将编译和打流的那个 shell 里按顺序设置一次。用 `ip -4 addr` 找到本机业务 IP 所在网卡，写入 `$nic_name`，再导出 `GLOO_SOCKET_IFNAME` 和 `TP_SOCKET_IFNAME`。`HCCL_SOCKET_IFNAME=eth,enp` 按前缀匹配，网卡名是 `enp...` 时不要改成单个网卡名。

```bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
source /usr/local/Ascend/driver/bin/setenv.bash
source /usr/local/Ascend/cann/set_env.sh

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/tools/mpich/lib/
export PATH=$PATH:/home/tools/mpich/bin
export PATH=/bin:$PATH

export HCCL_TOPO_FILE_PATH=/usr/local/Ascend/driver/topo/950/atlas_850_1.json
export HCCL_BUFFSIZE=1024
export HCCL_CONNECT_TIMEOUT=120
export HCCL_EXEC_TIMEOUT=200

export ASCEND_SLOG_PRINT_TO_STDOUT=0
export ASCEND_GLOBAL_LOG_LEVEL=3
export ASCEND_PROCESS_LOG_PATH=/home/hccl_test/logs/plog

export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=eth,enp
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=100
export HCCL_HOST_SOCKET_PORT_RANGE="auto"
```

`ASCEND_SLOG_PRINT_TO_STDOUT`：`1` 打屏，`0` 不打屏。`ASCEND_GLOBAL_LOG_LEVEL`：`0` debug，`1` info，`2` warning，`3` error。

## 4. 编译算子

沿用上一节的窗口，不要重新 source。**每一轮验收打流前**在参与该轮打流的每台机器上执行本节（跨机时 hostfile 内每台各做一遍），再用新算子打流；不要用环境里上次留下的 `mpich/bin` 旧二进制。

```bash
cd /usr/local/Ascend/ascend-toolkit/latest/tools/hccl_test
make clean 2>/dev/null || true
make -j$(nproc) MPI_HOME=/home/tools/mpich ASCEND_DIR=/usr/local/Ascend/ascend-toolkit/latest/aarch64-linux
cp -f /usr/local/Ascend/ascend-toolkit/latest/tools/hccl_test/bin/all_reduce_test \
      /usr/local/Ascend/ascend-toolkit/latest/tools/hccl_test/bin/all_gather_test \
      /usr/local/Ascend/ascend-toolkit/latest/tools/hccl_test/bin/alltoall_test \
      /home/tools/mpich/bin/
```

**全量性能测试**时在本机 `make` 完成后，将 `hccl_test/bin/` 下全部 `*_test` 可执行文件拷入 `mpich/bin`（与编译产物一致，例如 `all_gather_test`、`all_gatherv_test`、`all_reduce_test`、`alltoall_test`、`alltoallv_test`、`alltoallvc_test`、`broadcast_test`、`reduce_scatter_test`、`reduce_scatterv_test`、`reduce_test`、`scatter_test` 等）；第 7 节只跑其中 7 个算子，但拷全量可避免漏编。

在**当前这台机器**上执行（不要别机编完只 scp 二进制过来顶替本机编译）。`cp` 后核对：`stat` 显示 `mpich/bin` 与 `hccl_test/bin` 同名文件修改时间一致（或 `mpich/bin` 略晚）。打流命令应解析到 `/home/tools/mpich/bin/` 下**刚覆盖的文件**（写全路径），避免 PATH 里其它目录的旧算子。

说明：打流运行时 `source` 的是裸机 `cann/set_env.sh`（第 3 节）；算子编译仍用 **ascend-toolkit** 下 `tools/hccl_test` 与 `ASCEND_DIR=.../ascend-toolkit/latest/aarch64-linux`，与「用裸机 CANN 验收环境」不矛盾。

## 5. 单机打流

默认单机 8 卡。三条命令在已设置好环境的同一窗口里依次执行；`mpirun` 调用的 `all_reduce_test` / `all_gather_test` / `alltoall_test` 必须是 **本节开始前刚完成第 4 节 `cp` 的新算子**（见上节 `stat` 核对）。

```bash
# CCU
mpirun -n 8 all_reduce_test  -p 8 -b 64k -e 2g -f 2 -d int16 -a ccu_ms -t 1

# AIV
mpirun -n 8 all_gather_test  -p 8 -b 64k -e 2g -f 2 -d int16 -a aiv -t 1

# AICPU
mpirun -n 8 alltoall_test  -p 8 -b 64k -e 2g -f 2 -d int16 -a aicpu_ts
```

单机验收只看这三条。每条退出码为 0，且每一档 `check_result` 都是 `success`，才算该条通过。三条都通过，环境可用。

## 6. 跨机打流

跨机和单机是同一组打流场景，只是多了跨机参数：增加 `-f /home/tools/hostfile`，`-n` 改为总卡数，消息上限 `-e` 改为 `1g`。算子和 `-a` 与单机三条一致。机器数或每机卡数不同时，只改 hostfile 和 `-n`。

hostfile 每行 `IP:卡数`，执行打流命令的主机写第一条：

```text
192.0.2.101:8
192.0.2.102:8
192.0.2.x:8
```

文件放在 `/home/tools/hostfile`。`-n` 为总卡数，等于机器数乘每机卡数。两机 8 卡时 `-n 16`，`-p 8`。

下发 mpirun 之前，在每台机器上执行 `npu-smi info`。任一卡的进程表不为空，告诉用户哪台机器的哪张卡被哪个进程占用，停止打流，不要结束这些进程。

同时确认：

- 发起机能免密登录 hostfile 里的其他宿主机。出现 `REMOTE HOST IDENTIFICATION HAS CHANGED` 时，删掉 `known_hosts` 里该 IP 的旧行再重装公钥。`ssh-keygen -R` 因 `known_hosts` 有非法行失败时，直接删这些行，不要整文件替换失败后放弃
- 其他机器防火墙已关闭。未关闭且用户尚未同意时，先停下来说明，不要自行关防火墙
- 裸机跨机要求各机 `compiler/version.info` 全文一致，包括 `timestamp`。`Version=` 相同但 `timestamp` 不同仍是不同包。不一致时不要改宿主机 CANN，改用同一个镜像在每台机器起容器再打流
- 每台机器上的容器已挂载驱动目录、`/home`，且算子在 `/home/tools/mpich/bin`。1825 组网还要挂 `/etc/hccl_rootinfo.json`，非 1825 不要挂

每台机器都在本机 source `ascend-toolkit`、driver 和 `cann` 后再执行测试二进制。只在发起机设置 `LD_LIBRARY_PATH` 时，对端会找不到 `libhccl.so`。各机用自己业务 IP 所在网卡作为 `GLOO_SOCKET_IFNAME` 和 `TP_SOCKET_IFNAME`，`HCCL_SOCKET_IFNAME` 仍是 `eth,enp`。不要把发起机的网卡名传到对端。打流前把该机业务网卡名写入 `/home/hccl_test/nic_name`。容器里经常没有 `ip` 命令，不能只靠 `ip` 探测。

各机都放下面这个脚本，路径相同：`/home/tools/mpich/bin/with_cann_env`。

```bash
#!/bin/bash
source /usr/local/Ascend/ascend-toolkit/set_env.sh
source /usr/local/Ascend/driver/bin/setenv.bash
source /usr/local/Ascend/cann/set_env.sh
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/home/tools/mpich/lib/"
export PATH="${PATH}:/home/tools/mpich/bin"
export PATH="/bin:${PATH}"
export HCCL_TOPO_FILE_PATH=/usr/local/Ascend/driver/topo/950/atlas_850_1.json
export HCCL_BUFFSIZE=1024
export HCCL_CONNECT_TIMEOUT=120
export HCCL_EXEC_TIMEOUT=200
export ASCEND_SLOG_PRINT_TO_STDOUT=0
export ASCEND_GLOBAL_LOG_LEVEL=3
export ASCEND_PROCESS_LOG_PATH=/home/hccl_test/logs/plog
mkdir -p "$ASCEND_PROCESS_LOG_PATH"
if [ -f /home/hccl_test/nic_name ]; then
  nic_name=$(tr -d '[:space:]' < /home/hccl_test/nic_name)
elif command -v ip >/dev/null 2>&1; then
  nic_name=$(ip -4 -br addr | awk '$1 != "lo" && $1 !~ /^(docker|virbr)/ {print $1; exit}')
fi
export GLOO_SOCKET_IFNAME=$nic_name
export TP_SOCKET_IFNAME=$nic_name
export HCCL_SOCKET_IFNAME=eth,enp
export OMP_PROC_BIND=false
export OMP_NUM_THREADS=100
export HCCL_HOST_SOCKET_PORT_RANGE=auto
exec "$@"
```

裸机跨机用这个脚本包住测试二进制。`mpirun` 用 `/home/tools/mpich/bin/mpirun`。两机 8 卡示例：

```bash
# CCU
/home/tools/mpich/bin/mpirun -f /home/tools/hostfile -n 16 /home/tools/mpich/bin/with_cann_env all_reduce_test -b 64k -e 1g -f 2 -d int16 -p 8 -a ccu_ms -t 1

# AIV
/home/tools/mpich/bin/mpirun -f /home/tools/hostfile -n 16 /home/tools/mpich/bin/with_cann_env all_gather_test -b 64k -e 1g -f 2 -d int16 -p 8 -a aiv -t 1

# AICPU
/home/tools/mpich/bin/mpirun -f /home/tools/hostfile -n 16 /home/tools/mpich/bin/with_cann_env alltoall_test -b 64k -e 1g -f 2 -d int16 -p 8 -a aicpu_ts
```

容器跨机用同一个镜像、同一个容器名 `hccl-dual`。不要把宿主机 `cann` 目录挂进容器。各机再放 `/home/tools/mpich/bin/enter_hccl_dual`：

```bash
#!/bin/bash
exec docker exec hccl-dual /home/tools/mpich/bin/with_cann_env "$@"
```

`--network host` 下容器与宿主机共用 IP 和主机名，光看 `hostname` 或 IP 分不出 rank 到底落在哪。跨机打流前先做一次执行环境自证，各机放 `/home/tools/mpich/bin/verify_in_container`：

```bash
#!/bin/bash
cg=$(head -1 /proc/1/cgroup | sed 's/^[0-9]*:[^:]*://')
if echo "$cg" | grep -q docker; then where="CONTAINER"; else where="BARE-METAL"; fi
echo "${where} host=$(cat /proc/sys/kernel/hostname) rootfs=$(stat -f -c %T /) cann=$(grep -m1 '^Version=' /usr/local/Ascend/cann/compiler/version.info 2>/dev/null | cut -d= -f2)"
```

```bash
/home/tools/mpich/bin/mpirun -f /home/tools/hostfile -n 16 /home/tools/mpich/bin/enter_hccl_dual /home/tools/mpich/bin/verify_in_container
```

每个 rank 都必须输出 `CONTAINER` 和 `rootfs=overlayfs`。只要有一个 rank 输出 `BARE-METAL` 或 `rootfs=ext2/ext3`，说明它没进容器，停止打流先排查。`rootfs` 是最可靠的判据；`cann` 字段在宿主机与镜像版本不同时是额外佐证，两边版本恰好相同时它不区分。

容器内再核对两边 `version.info` 的 `Version` 和 `timestamp` 一致，然后打流：

```bash
# CCU
/home/tools/mpich/bin/mpirun -f /home/tools/hostfile -n 16 /home/tools/mpich/bin/enter_hccl_dual all_reduce_test -b 64k -e 1g -f 2 -d int16 -p 8 -a ccu_ms -t 1

# AIV
/home/tools/mpich/bin/mpirun -f /home/tools/hostfile -n 16 /home/tools/mpich/bin/enter_hccl_dual all_gather_test -b 64k -e 1g -f 2 -d int16 -p 8 -a aiv -t 1

# AICPU
/home/tools/mpich/bin/mpirun -f /home/tools/hostfile -n 16 /home/tools/mpich/bin/enter_hccl_dual alltoall_test -b 64k -e 1g -f 2 -d int16 -p 8 -a aicpu_ts
```

打流进行中还可以从宿主机侧独立取证，确认进程的根文件系统就是容器 overlay：

```bash
p=$(for q in $(ls /proc | grep -E '^[0-9]+$'); do [ "$(cat /proc/$q/comm 2>/dev/null)" = all_reduce_test ] && echo $q; done | head -1)
grep -m1 ' / ' /proc/$p/mountinfo
grep -m1 -o '/[^ ]*libhccl[^ ]*' /proc/$p/maps
```

第一条应出现 `overlay` 和 `upperdir=/…/overlay2/<id>/diff`；第二条的路径应指向镜像自带的 `cann` 目录（宿主机上通常没有这个目录）。两条都对，才说明打的是容器里那份 CANN。

不要用 `readlink /proc/$p/root` 判断：容器进程这里返回 `/`，看不出是不是容器，`mountinfo` 才准。

跨机同样以这三条都通过为环境可用。

## 7. 全量性能测试（可选）

用户明确要求 **全量性能测试**、**全算子打流**、**性能报告** 等时执行本节。本节 **不判定**「环境可用」（仍以第 5 / 6 节三条为准）。

### 7.1 算子与二进制

| 集合通信（用户口径） | 测试二进制（`mpich/bin` 下） |
| --- | --- |
| alltoall | `alltoall_test` |
| alltoallv | `alltoallv_test` |
| reducescatter | `reduce_scatter_test` |
| allgather | `all_gather_test` |
| allreduce | `all_reduce_test` |
| broadcast | `broadcast_test` |
| reduce | `reduce_test` |

每个算子跑 **两条**：**AIV**（`-a aiv -t 1`）与 **AICPU**（`-a aicpu_ts`）。共 **14 条**打流。参数与其余字段同验收：**单机** `-n 8 -p 8 -b 64k -e 2g -f 2 -d int16`；**跨机**加 `-f /home/tools/hostfile`，`-n` 为总卡数，`-e 1g`，`-p 8`。环境与包装同第 6 节：`/home/tools/mpich/bin/mpirun`、`/home/tools/mpich/bin/with_cann_env`、算子写全路径。

**AIV 示例（跨机，替换 `<N>` 与算子名）：**

```bash
/home/tools/mpich/bin/mpirun -f /home/tools/hostfile -n <N> /home/tools/mpich/bin/with_cann_env all_reduce_test -b 64k -e 1g -f 2 -d int16 -p 8 -a aiv -t 1
```

**AICPU 示例：**

```bash
/home/tools/mpich/bin/mpirun -f /home/tools/hostfile -n <N> /home/tools/mpich/bin/with_cann_env all_reduce_test -b 64k -e 1g -f 2 -d int16 -p 8 -a aicpu_ts
```

按上表替换 `all_reduce_test` 为对应二进制即可；**不要**在全量 14 条里使用验收专用的 CCU `-a ccu_ms`。

建议执行顺序（每条先 AIV 再 AICPU，或先算子后后端，全程固定一种顺序并在报告头写明）：alltoall → alltoallv → reducescatter → allgather → allreduce → broadcast → reduce。

### 7.2 报告输出（勿整段刷屏）

全量 14 条原始输出过长，**默认不写进聊天长文**；在用户指定的目录生成 **一份 Markdown 报告**（推荐 **`.md`**，不用纯 `.txt`：便于 `##` 目录、在 IDE / GitCode 预览、代码块折叠阅读）。用户坚持时要可同时写同名 `.txt`（与 `.md` 正文相同）。

- 路径：`<用户指定目录>/hccl_fullperf_<场景简述>_<YYYYMMDD_HHMMSS>.md`（例如 `hccl_fullperf_cross32_20261010_095113.md`）。
- 报告开头用列表写清：验收类型（全量性能）、单机/跨机、hostfile、`n`、CANN 路径、各机是否已按第 4 节新编译、非 1825 是否已处理 rootinfo。
- 每一条一个小节，标题格式：`### AIV — alltoall_test（-a aiv -t 1）` 或 `### AICPU — alltoall_test（-a aicpu_ts）`。
- 小节内一个 ` ```text ` 代码块：**第一行起为完整打流命令**，空一行，之后为工具原始输出（从 `the minbytes is` 到最后一档 `check_result`，不删列、不汇总带宽表）。
- 某条失败：该节仍记录命令；输出只写在报告里供排查，**聊天里**按「结果记录」说明原因，不贴长 log。

打流结束后告知用户 **报告绝对路径**；聊天可只给每条是否 success 的一行索引表，除非用户要求打开某一条全文。

## 故障定位

先看本次打流写出的日志。日志目录是当前环境的 `ASCEND_PROCESS_LOG_PATH`。裸机打流默认 `/home/hccl_test/logs/plog`，vLLM 容器拉起命令里是 `/home/hccl_test/logs_pd`。只看这次进程启动之后的文件。不要用 `/root/ascend/log` 里更早的 ERROR 下结论。

多机打流时，报错日志只出现在有问题的那台机器上。发起机没有 ERROR，不能说明其他机器正常。hostfile 里的每台机器都要查同一日志目录。容器打流时，日志在容器里的 `ASCEND_PROCESS_LOG_PATH`；该目录挂在 `/home` 下时，宿主机上的相同路径就是容器里的日志。

```bash
grep -rn ERROR "$ASCEND_PROCESS_LOG_PATH"
```

按报错内容处理。未出现对应报错时不要执行该项修复。

### 卡被占用

报错显示卡被占用时，执行：

```bash
npu-smi info
```

看进程表，不看 `docker ps`。进程表为空时，卡没有被占用；已有容器处于 Up 只说明设备曾经挂进容器，不代表不能打流。进程表里该卡已有进程时，告知用户卡被占用，无法打流。不要结束这些进程。

### eid 匹配不上

只有 1825 组网 才需要 `/etc/hccl_rootinfo.json`。确认是 1825 后，检查它是否存在，不存在则生成并拷贝到 `/etc/`，容器打流还要把它挂进容器。非 1825 组网不要使用或挂载它，挂了反而可能导致打流报错（2026-10-09 在 128↔129 双机容器上不挂它，三条验收全过）。下载工具时网络不通，先问用户要代理，不要换源硬装。

非 1825 且日志里是 `DeserializeLevelList`、`DetectRankTable`、`root_info_detect_provider` 或 `hccl_test_common.cc:901 retcode:4` 而无 eid 字面时：先查该机是否仍留有 `/etc/hccl_rootinfo.json`；有则在用户同意下移走备份后重打单机三条，不要按本节去 `mindcluster-tools rootinfo` 生成。

```bash
pip install --force-reinstall --upgrade unofficial-ascend-tools
mindcluster-tools rootinfo --output hccl_rootinfo.json --max_level 2
```

生成后的 `hccl_rootinfo.json` 拷贝到 `/etc/`。

### tls 报错

关闭证书校验：

```bash
hccn_tool -s -tls -i 0 -enable 0
```

### jfc 报错

检查是否已经写过 `/etc/modprobe.d/udma.conf`。没有则写入，然后重启。重启前向用户说明并取得同意。

```bash
cat << EOF > /etc/modprobe.d/udma.conf
options udma dfx_switch=1 fast_destroy_tp=0 jfc_arm_mode=2
EOF
```

### 跨机 CANN 版本不一致

不同机器的宿主机 CANN 包版本不同会导致 `RootInfoDetect` 失败，日志里是 `SetupAgent fail` 或 `client recv fail`。对比各机 `version.info` 全文，包括 `timestamp`。不一致时不要更换宿主机 CANN。两边用同一个镜像起容器，容器里的 CANN 就是同一份，再在容器里打流。未指定镜像时用两边都已有的同一个 `vllm-ascend` 标签，不要自己拉新镜像。CANN 不在默认路径时，把下面路径换成用户给的安装路径。

```bash
cat /usr/local/Ascend/cann/compiler/version.info
```

裸机跨机遇到版本不一致时基本是立刻失败：`hccl_allreduce_rootinfo_test.cc:<行号>, retcode: 2`，一条 `success` 都没有。所以「裸机报错、同样命令换成容器后全过」本身就是一次有效的判别，说明成功的那次确实在容器里。

### 缩小范围

跨机打不通时，先保证单机正常，再按双机、三机、四机往上加，找出是哪一台加进来之后不通。

单机不通时，用指定卡打流排除是哪张卡有问题。`-genv ASCEND_RT_VISIBLE_DEVICES` 写卡号，`-n` 与 `-p` 写卡数：

```bash
mpirun -genv ASCEND_RT_VISIBLE_DEVICES 1,2,3,4,6,7 -n 6 all_gather_test -p 6 -b 64k -e 2g -f 2 -d int16
```

指定卡命令用来定位故障卡，不代替单机三条验收。

## 结果记录

退出码为 0 且每一档 `check_result` 都是 `success`，该条才算通过。

### 环境可用验收（三条）

成功时，**先贴该条实际执行的完整打流命令**（含 `mpirun` 路径、`-f hostfile`、`-n`、算子全路径或 `with_cann_env` 包装、全部参数），**再贴**该命令的原始输出。格式示例：一行标题（如 `AICPU — alltoall_test（-a aicpu_ts）`），接着 fenced 代码块里先命令、空一行、再 `the minbytes is...` 起的工具输出。多 rank 输出交错时也原样贴，不要挑一个 rank 重排，不要改成表格，不要增删列，不要加带宽摘要。三条都通过时给出「环境可用」。

失败时，不要把打流命令的输出贴给用户。停止后续验收，按「故障定位」查出原因，直接告诉用户错误原因和如何修复。

### 全量性能测试（14 条）

按第 7.2 节写入用户目录下的 **`.md` 报告**（每条：标题 + 命令 + 原始输出）。聊天回复报告路径；可选附 14 行以内的通过/失败索引。全量某条失败不自动否定「环境可用」，但若三条验收未做过，应提醒用户先跑验收。
