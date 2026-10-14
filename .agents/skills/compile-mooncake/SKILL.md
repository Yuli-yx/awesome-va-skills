---
name: compile-mooncake
description: Compiles Mooncake with USE_ASCEND_DIRECT on openEuler aarch64 Ascend containers, then copies libmooncake_common.so, libtransfer_engine.so, and libmooncake_store.so into CANN python site-packages. Use when the user asks to compile Mooncake, build Mooncake, 编译 mooncake, make install Mooncake, USE_ASCEND_DIRECT, or install Mooncake .so into ascend-toolkit.
---

# Compile Mooncake (Ascend Direct / openEuler)

Run this workflow on the **target Linux container**, not on Windows. Treat paths as runtime inputs, not fixed machine-wide defaults:

| Item | Default |
| --- | --- |
| Source | User-provided checkout; otherwise the current directory when it is a Mooncake repo |
| CANN | User-provided `CANN_ROOT`; otherwise the already active `ASCEND_HOME_PATH` or a detected common install |
| Install dest | Auto-detected `python/site-packages/mooncake/` inside the selected CANN tree; override with `DEST` |
| yalantinglibs | Prefer the checkout's pinned `extern/yalantinglibs` submodule; use explicit `YLT_SRC` only as a fallback |
| Proxy | Explicit `PROXY_IP`, or select the user's current local-computer address by the target server's leading network family; port `3128` |

Always prefer paths supplied by the user and verify them inside the target container. Source only the selected CANN installation, print the resolved `ASCEND_HOME_PATH`, and avoid mixing headers or libraries from another CANN tree. Set `CANN_REQUIRED_VERSION` only when the task requires an exact version.

## Proxy selection

These proxy addresses are the user's current local-computer IPs and can change after that computer restarts:

- target server in the `141.*.*.*` network family -> `141.4.152.201`
- target server in the `80.*.*.*` network family -> `80.254.137.250`
- target server in the `90.*.*.*` network family -> `90.254.35.230`

An explicit `PROXY_IP` always wins. Otherwise, choose by the first IPv4 octet of the SSH target or `TARGET_SERVER_IP`; container addresses can be unrelated bridge addresses. Probe the selected proxy before installing dependencies. If no network family matches or the proxy probe fails, stop and tell the user which address failed; ask the user for the current proxy IP instead of guessing or falling back to a stale address. Use `PROXY_IP=none` only when the user explicitly wants a direct-network build.

## Do not

- Assume a CANN path or version from a previous machine. Inspect the current container and honor the user's selected `CANN_ROOT`.
- Mix `set_env.sh`, headers, or libraries from different CANN installations.
- Run repo-root `dependencies.sh` (RHEL package names; fails on openEuler).
- Use Debian multiarch paths (`/usr/lib/aarch64-linux-gnu`, `CPATH=.../mpich`).
- Enable `-DUSE_ETCD=ON` / `-DSTORE_USE_ETCD=ON` unless the user explicitly wants etcd **and** Go TLS works (`GOTOOLCHAIN=local` is not enough if go.mod pins a missing toolchain).
- Enable `-DWITH_STORE_RUST=ON` (no rustc in this image).
- Override the checkout-pinned `yalantinglibs` version without evidence that the source requires it.
- Treat a later vLLM `set_device` / E30009 signature error as a Mooncake link failure.

`sed` on `USE_ASCEND_DIRECT` is unnecessary; pass `-DUSE_ASCEND_DIRECT=ON`.

## How to run

1. Enter the container (typical: `docker exec -it 1825-new-test bash` on the NPU host).
2. Copy [scripts/build_mooncake.sh](scripts/build_mooncake.sh) into the container (or write it there) and execute it as root.
3. If the agent is on a jump host, SSH in and `docker exec` the script; do not compile on Windows.

```bash
MOONCAKE_SRC=/path/to/Mooncake \
CANN_ROOT=/path/to/CANN/install \
TARGET_SERVER_IP=<ssh-target-ip> \
bash /path/to/build_mooncake.sh
```

When the target server address is known to the agent, pass `TARGET_SERVER_IP` or select the matching proxy above and pass it explicitly, for example `PROXY_IP=80.254.137.250 bash /path/to/build_mooncake.sh`. Useful env overrides: `MOONCAKE_SRC`, `CANN_ROOT`, `CANN_REQUIRED_VERSION`, `DEST`, `YLT_SRC`, `MSGPACK_SRC`, `INSTALL_LIBDIR`, `TARGET_SERVER_IP`, `PROXY_IP`, `PROXY_PORT`, and `CLEAN_BUILD=0` for a compatible incremental retry.

If the script cannot be copied, follow **Manual steps** below in order. Prefer the checkout's own openEuler dependency installer and pinned submodules; use older fallbacks only when the current source actually needs them.

## Manual steps

### 0. Proxy, TLS, PATH

```bash
TARGET_SERVER_IP="${TARGET_SERVER_IP:-$(hostname -I 2>/dev/null || true)}"
if [[ -n "${PROXY_IP:-}" ]]; then
  IP="$PROXY_IP"
elif grep -qE '(^|[[:space:]])141\.' <<<"$TARGET_SERVER_IP"; then
  IP="141.4.152.201"
elif grep -qE '(^|[[:space:]])80\.' <<<"$TARGET_SERVER_IP"; then
  IP="80.254.137.250"
elif grep -qE '(^|[[:space:]])90\.' <<<"$TARGET_SERVER_IP"; then
  IP="90.254.35.230"
else
  echo "Cannot select the proxy from this server's network. Ask the user for the current proxy IP." >&2
  exit 1
fi
PORT="${PROXY_PORT:-3128}"
HTTP_CODE="$(curl -ksS -o /dev/null -w '%{http_code}' --connect-timeout 3 --max-time 8 \
  --proxy "http://$IP:$PORT" https://github.com/ || true)"
if [[ "$HTTP_CODE" == "000" || -z "$HTTP_CODE" ]]; then
  echo "Proxy http://$IP:$PORT is unreachable. Ask the user for the current proxy IP." >&2
  exit 1
fi
export http_proxy="http://$IP:$PORT" https_proxy="http://$IP:$PORT"
export HTTP_PROXY="$http_proxy" HTTPS_PROXY="$http_proxy"
export no_proxy="127.0.0.1,localhost,local,.local,*.huawei.com"
export NO_PROXY="$no_proxy"
export GIT_SSL_NO_VERIFY=true CMAKE_TLS_VERIFY=0
export GOTOOLCHAIN=local GOPROXY=https://goproxy.cn,https://goproxy.io,direct GOSUMDB=off
export PATH="/usr/local/go/bin:/usr/local/python3.11.10/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
```

### 1. Source the selected CANN tree

```bash
if [[ -f "$CANN_ROOT/set_env.sh" ]]; then
  source "$CANN_ROOT/set_env.sh"
elif [[ -f "$CANN_ROOT/cann/set_env.sh" ]]; then
  source "$CANN_ROOT/cann/set_env.sh"
  [[ -f "$CANN_ROOT/ascend-toolkit/set_env.sh" ]] && \
    source "$CANN_ROOT/ascend-toolkit/set_env.sh"
else
  echo "No set_env.sh under CANN_ROOT=$CANN_ROOT" >&2
  exit 1
fi
echo "ASCEND_HOME_PATH=$ASCEND_HOME_PATH"
```

### 2. openEuler packages

```bash
cd "$MOONCAKE_SRC"
bash scripts/ascend/dependencies_openeuler.sh -y
```

Package name is `boost-devel`, not `boost1.78-devel`.

### 3. Source-provided openEuler dependencies

```bash
bash scripts/ascend/dependencies_openeuler.sh -y
```

Recent checkouts initialize their pinned submodules and install `yalantinglibs` here. Verify the packages required by the current `find_package(...)` calls before configuring Mooncake. If this installer fails only while downloading Go but the Mooncake configuration disables ETCD/Go, verify the required C/C++ postconditions and continue; do not make the optional Go toolchain a false build blocker. Do not blindly run `dependencies_ascend_installation.sh`: some revisions use `set +e` and undefined working-directory variables on yum systems.

If the current source references `msgpack.hpp` but the header is missing, install pinned `msgpack-c` tag `cpp-7.0.0`. CMake 3.31 may fail on `FIND_PACKAGE(Boost)` (CMP0167), so build it with:

```bash
yum install -y boost-devel
cd /path/to/msgpack-c
git checkout cpp-7.0.0
rm -rf build && mkdir build && cd build
cmake .. -DMSGPACK_USE_BOOST=OFF -DMSGPACK_BUILD_DOCS=OFF \
         -DMSGPACK_BUILD_EXAMPLES=OFF -DMSGPACK_BUILD_TESTS=OFF
make -j"$(nproc)" && make install
test -f /usr/local/include/msgpack.hpp
```

`MSGPACK_*` flags are **only** for msgpack-c, not for Mooncake cmake.

### 4. Unversioned `.so` symlinks (overlay/rpm gap)

```bash
[ -e /usr/lib64/libcurl.so ]    || ln -sf libcurl.so.4    /usr/lib64/libcurl.so
[ -e /usr/lib64/libhiredis.so ] || ln -sf libhiredis.so.1 /usr/lib64/libhiredis.so
[ -e /usr/lib64/libnuma.so ]    || ln -sf libnuma.so.1    /usr/lib64/libnuma.so
ldconfig
test -f /usr/lib64/cmake/gflags/gflags-config.cmake
test -f /usr/include/json/json.h
test -e /usr/lib64/libjsoncpp.so
```

### 5. yalantinglibs

Prefer `git submodule update --init --recursive` and build the revision pinned by the Mooncake checkout. If the checkout has no pinned submodule, use a user-provided `YLT_SRC`; do not silently substitute a version remembered from another Mooncake revision.

### 6. cmake + ninja

```bash
cd "$MOONCAKE_SRC"
rm -rf build && mkdir build && cd build

cmake .. -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DUSE_ASCEND_DIRECT=ON -DUSE_CUDA=OFF -DWITH_EP=OFF \
  -DBUILD_SHARED_LIBS=ON -DBUILD_UNIT_TESTS=OFF -DBUILD_EXAMPLES=OFF \
  -DUSE_HTTP=ON -DUSE_ETCD=OFF -DSTORE_USE_ETCD=OFF \
  -DWITH_STORE_RUST=OFF -DWITH_STORE_GO=OFF \
  -Dgflags_DIR=/usr/lib64/cmake/gflags \
  -DJSONCPP_INCLUDE_DIR=/usr/include \
  -DJSONCPP_LIBRARY=/usr/lib64/libjsoncpp.so \
  -DCMAKE_PREFIX_PATH="/usr;/usr/local" \
  -DCMAKE_TLS_VERIFY=0

ninja
ninja install
```

Link against `$ASCEND_HOME_PATH/aarch64-linux/lib64/libmetadef.so`.

### 7. Copy the three `.so` files (regular files, not symlinks)

```bash
DEST="${DEST:-$ASCEND_HOME_PATH/python/site-packages/mooncake}"
test -d "$(dirname "$DEST")"
mkdir -p "$DEST"
cp -f \
  "${INSTALL_LIBDIR:-/usr/local/lib}/libmooncake_common.so" \
  "${INSTALL_LIBDIR:-/usr/local/lib}/libtransfer_engine.so" \
  "${INSTALL_LIBDIR:-/usr/local/lib}/libmooncake_store.so" \
  "$DEST/"
ldconfig
ls -lh "$DEST"/libmooncake_common.so "$DEST"/libtransfer_engine.so "$DEST"/libmooncake_store.so
```

Resolve `DEST` before copying and report its canonical path. Copy the install-tree libraries produced by `cmake --install`, not raw build-tree libraries: build-tree RPATH entries can retain absolute paths into the temporary build directory. The default install library directory is `/usr/local/lib`; override `INSTALL_LIBDIR` when the CMake install prefix differs.

Expected RelWithDebInfo sizes (approx): common 7.9M, transfer_engine 32M, store 388M.

## Done when

- `ninja` and `ninja install` succeeded.
- The three `.so` files exist under the CANN `site-packages/mooncake/` dest above.
- `readelf -d` shows no RPATH/RUNPATH entry back into the Mooncake build directory.
- `ldd` reports no unresolved dependency and Ascend libraries resolve to the selected CANN tree.
- Run a minimal package/extension import as a separate runtime check and report its process exit code; a successful build does not hide an import or unload-time failure.
- Tell the user those paths and sizes. Do not start vLLM unless asked.

## Extra troubleshooting

See [reference.md](reference.md).
