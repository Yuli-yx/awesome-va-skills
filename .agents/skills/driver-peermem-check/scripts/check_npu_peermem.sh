#!/bin/bash
# 检查 Ascend 驱动包中 npu_peermem.ko 相关内容
# 用法: bash check_npu_peermem.sh <extract_dir> [package_name]
#
# 输出包含四部分:
#   [SUMMARY]  一行摘要
#   [CHECKLIST] 逐项检查结果
#   [BUILD_DEPS] 如果存在源码，输出构建依赖分析
#   [CONCLUSION] 最终判断

set -euo pipefail

EXTRACT_DIR="${1:-}"
PKG_NAME="${2:-$(basename "$EXTRACT_DIR")}"

if [[ -z "$EXTRACT_DIR" || ! -d "$EXTRACT_DIR" ]]; then
    echo "用法: bash check_npu_peermem.sh <extract_dir> [package_name]"
    echo "错误: 提取目录不存在或未指定"
    exit 1
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass()  { echo -e "${GREEN}[PASS]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
info()  { echo -e "       $*"; }

# ---------- 查找 ko 文件 ----------
KO_FILE=""
KO_PATH="${EXTRACT_DIR}/driver/host/npu_peermem.ko"
KO_ALT=$(find "$EXTRACT_DIR" -name "npu_peermem.ko" -type f 2>/dev/null | head -1 || true)

# ---------- 查找源码 ----------
NDR_DIR=""
NDR_PATH="${EXTRACT_DIR}/driver/kernel/ndr"
NDR_ALT=$(find "$EXTRACT_DIR" -path "*/kernel/ndr" -type d 2>/dev/null | head -1 || true)

# ---------- 脚本引用 ----------
DEAL_KO="${EXTRACT_DIR}/driver/script/deal_ko.sh"
HOT_RESET="${EXTRACT_DIR}/driver/script/device_hot_reset.sh"
SPEC_FUNC="${EXTRACT_DIR}/driver/script/specific_func.inc"

echo "=============================================="
echo " npu_peermem.ko 驱动包检查报告"
echo " 包名: ${PKG_NAME}"
echo "=============================================="
echo ""

# ==================== [SUMMARY] ====================
echo "[SUMMARY]"

# 检查 ko 文件
HAS_KO=false
if [[ -n "$KO_ALT" ]]; then
    HAS_KO=true
    KO_FILE="$KO_ALT"
fi
if [[ -f "$KO_PATH" ]]; then
    HAS_KO=true
    KO_FILE="$KO_PATH"
fi

# 检查源码
HAS_SRC=false
if [[ -n "$NDR_ALT" ]]; then
    NDR_DIR="$NDR_ALT"
fi
if [[ -d "$NDR_PATH" ]]; then
    NDR_DIR="$NDR_PATH"
fi
if [[ -n "$NDR_DIR" && -f "$NDR_DIR/npu_peermem.c" ]]; then
    HAS_SRC=true
fi

if $HAS_KO; then
    KO_SIZE=$(ls -lh "$KO_FILE" 2>/dev/null | awk '{print $5}')
    echo "  npu_peermem.ko: 存在 (${KO_SIZE}, ${KO_FILE})"
else
    echo "  npu_peermem.ko: 不存在"
fi

if $HAS_SRC; then
    SRC_COUNT=$(ls "$NDR_DIR"/*.{c,h,sh} 2>/dev/null | wc -l)
    echo "  npu_peermem 源码: 存在 (${SRC_COUNT} 个文件, ${NDR_DIR}/)"
else
    echo "  npu_peermem 源码: 不存在"
fi

echo ""

# ==================== [CHECKLIST] ====================
echo "[CHECKLIST]"

# 1. ko 文件
if $HAS_KO; then
    pass "driver/host/npu_peermem.ko — 已编译模块存在"
else
    fail "driver/host/npu_peermem.ko — 已编译模块缺失"
fi

# 2. 源码
if $HAS_SRC; then
    pass "driver/kernel/ndr/npu_peermem.c — 源码存在"
else
    warn "driver/kernel/ndr/npu_peermem.c — 源码缺失"
fi

# 3. peer_mem.h
if [[ -f "${NDR_DIR:-/nonexistent}/peer_mem.h" ]]; then
    pass "driver/kernel/ndr/peer_mem.h — 头文件存在"
elif $HAS_SRC; then
    fail "driver/kernel/ndr/peer_mem.h — 头文件缺失（源码目录中缺少）"
else
    warn "driver/kernel/ndr/peer_mem.h — 无源码目录，跳过"
fi

# 4. deal_ko.sh
if [[ -f "$DEAL_KO" ]]; then
    if grep -q "npu_peermem" "$DEAL_KO" 2>/dev/null; then
        EXCLUDE_LINE=$(grep "npu_peermem" "$DEAL_KO" | head -1)
        if echo "$EXCLUDE_LINE" | grep -qE 'grep.*-v|grep.*-Ev'; then
            warn "deal_ko.sh 中 npu_peermem 被显式排除"
            info "$EXCLUDE_LINE"
        else
            pass "deal_ko.sh 引用了 npu_peermem"
            info "$EXCLUDE_LINE"
        fi
    else
        warn "deal_ko.sh 未引用 npu_peermem"
    fi
else
    warn "driver/script/deal_ko.sh — 文件不存在"
fi

# 5. device_hot_reset.sh
if [[ -f "$HOT_RESET" ]]; then
    if grep -q "npu_peermem" "$HOT_RESET" 2>/dev/null; then
        pass "device_hot_reset.sh 有 npu_peermem 防御性检查"
    else
        warn "device_hot_reset.sh 未引用 npu_peermem"
    fi
else
    warn "driver/script/device_hot_reset.sh — 文件不存在"
fi

# 6. specific_func.inc
if [[ -f "$SPEC_FUNC" ]]; then
    if grep -q "npu_peermem" "$SPEC_FUNC" 2>/dev/null; then
        pass "specific_func.inc 中 npu_peermem 在标准模块列表中"
    else
        info "specific_func.inc 中 npu_peermem 不在标准模块列表（非标准模块）"
    fi
else
    warn "driver/script/specific_func.inc — 文件不存在"
fi

echo ""

# ==================== [BUILD_DEPS] ====================
if $HAS_SRC && [[ -f "$NDR_DIR/Makefile" ]]; then
    echo "[BUILD_DEPS]"
    echo "  源码目录: ${NDR_DIR}"

    # 列出文件
    echo "  文件清单:"
    for f in "$NDR_DIR"/*; do
        echo "    - $(basename "$f") ($(wc -c < "$f" 2>/dev/null || echo '?') bytes)"
    done

    echo ""
    echo "  编译依赖:"

    if grep -q "HIAI_DKMS_DIR" "$NDR_DIR/Makefile" 2>/dev/null; then
        echo "    - HIAI_DKMS_DIR (Ascend DKMS 头文件路径)"
    fi
    if grep -q "OFA_SYMVERS_DIR" "$NDR_DIR/Makefile" 2>/dev/null; then
        echo "    - OFA_SYMVERS_DIR (OFED Module.symvers 路径)"
    fi
    if grep -q "IB_PEER_MEM_SYMBOLS_PRESENT" "$NDR_DIR/Makefile" 2>/dev/null; then
        echo "    - 条件编译: IB_PEER_MEM_SYMBOLS_PRESENT (需 OFED 符号文件)"
    fi
    if grep -q "CFG_SOC_PLATFORM" "$NDR_DIR/Makefile" 2>/dev/null; then
        PLATFORM=$(grep "CFG_SOC_PLATFORM" "$NDR_DIR/Makefile" | head -1)
        echo "    - 平台: $(echo "$PLATFORM" | awk -F'=' '{print $NF}')"
    fi

    # find_ofed_symvers.sh 搜索路径
    if [[ -f "$NDR_DIR/find_ofed_symvers.sh" ]]; then
        echo "    - OFED 搜索路径:"
        grep -E '/usr/src|/var/lib' "$NDR_DIR/find_ofed_symvers.sh" 2>/dev/null | sed 's/.*/      &/' || true
    fi

    echo ""
    echo "  编译命令 (目标机器上):"
    echo "    export HIAI_DKMS_DIR=<ascend-driver-source-root>"
    echo "    export OFA_SYMVERS_DIR=<ofed-module-symvers-dir>"
    echo "    make -C /lib/modules/\$(uname -r)/build M=${NDR_DIR} modules"
fi

echo ""

# ==================== [CONCLUSION] ====================
echo "[CONCLUSION]"

VER=$(echo "$PKG_NAME" | grep -oP '\d+\.\d+\.[^_]*' | head -1 || echo "未知")
ARCH=$(echo "$PKG_NAME" | grep -oP '(x86-64|aarch64)' | head -1 || echo "未知")
PLATFORM=$(echo "$PKG_NAME" | grep -oP 'Atlas-A\d+' | head -1 || echo "未知")

echo "  平台:    ${PLATFORM}"
echo "  版本:    ${VER}"
echo "  架构:    ${ARCH}"

if $HAS_KO; then
    echo "  结论:    npu_peermem.ko 已编译并包含在包中"
    echo "  影响:    d2d/d2rd RDMA 传输可用"
elif $HAS_SRC; then
    echo "  结论:    有源码但无预编译 .ko，需在目标机器上编译"
    echo "  影响:    d2d/d2rd RDMA 传输在编译安装前不可用"
    echo "  操作:    参见上方 [BUILD_DEPS] 编译命令"
else
    echo "  结论:    驱动包不含 npu_peermem.ko 及其源码"
    echo "  影响:    d2d/d2rd RDMA 传输不可用，仅 h2h 可用"
    echo "  可能原因:"
    echo "    - 新版驱动中功能已合并到其他模块（如 drv_pcie_host.ko）"
    echo "    - 该模块需要 OFED 环境单独编译，不再随驱动包分发"
    echo "    - 平台不支持"
fi

echo ""
echo "=============================================="
