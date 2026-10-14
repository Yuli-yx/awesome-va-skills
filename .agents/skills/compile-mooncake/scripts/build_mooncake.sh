#!/usr/bin/env bash
# Build Mooncake with USE_ASCEND_DIRECT on openEuler aarch64.
# Run inside the target container as root. See ../SKILL.md.
set -euo pipefail

MOONCAKE_SRC="${MOONCAKE_SRC:-}"
CANN_ROOT="${CANN_ROOT:-}"
CANN_REQUIRED_VERSION="${CANN_REQUIRED_VERSION:-}"
YLT_SRC="${YLT_SRC:-/tmp/yalantinglibs-src}"
MSGPACK_SRC="${MSGPACK_SRC:-/tmp/msgpack-c-src}"
INSTALL_LIBDIR="${INSTALL_LIBDIR:-/usr/local/lib}"
PROXY_PORT="${PROXY_PORT:-3128}"
TARGET_SERVER_IP="${TARGET_SERVER_IP:-}"
DEST="${DEST:-}"
CLEAN_BUILD="${CLEAN_BUILD:-1}"

log() { echo "[$(date '+%F %T')] $*"; }

if [[ -z "$MOONCAKE_SRC" ]]; then
  if [[ -f "$PWD/CMakeLists.txt" && -d "$PWD/mooncake-common" ]]; then
    MOONCAKE_SRC="$PWD"
  else
    echo "Set MOONCAKE_SRC to the Mooncake checkout." >&2
    exit 1
  fi
fi
if [[ ! -d "$MOONCAKE_SRC" ]]; then
  echo "Mooncake source not found: $MOONCAKE_SRC" >&2
  exit 1
fi

if [[ -z "$CANN_ROOT" ]]; then
  for candidate in "${ASCEND_HOME_PATH:-}" \
    /usr/local/Ascend/ascend-toolkit/latest /usr/local/Ascend/cann; do
    if [[ -n "$candidate" && -d "$candidate" ]]; then
      CANN_ROOT="$candidate"
      break
    fi
  done
fi
if [[ -z "$CANN_ROOT" || ! -d "$CANN_ROOT" ]]; then
  echo "Set CANN_ROOT to the active CANN installation or bundle root." >&2
  exit 1
fi
CANN_ROOT="${CANN_ROOT%/}"

set +u
if [[ -f "$CANN_ROOT/set_env.sh" ]]; then
  # shellcheck disable=SC1090
  source "$CANN_ROOT/set_env.sh"
elif [[ -f "$CANN_ROOT/cann/set_env.sh" ]]; then
  # shellcheck disable=SC1090
  source "$CANN_ROOT/cann/set_env.sh"
  if [[ -f "$CANN_ROOT/ascend-toolkit/set_env.sh" ]]; then
    # shellcheck disable=SC1090
    source "$CANN_ROOT/ascend-toolkit/set_env.sh"
  fi
elif [[ -z "${ASCEND_HOME_PATH:-}" ]]; then
  echo "No set_env.sh found under CANN_ROOT=$CANN_ROOT and ASCEND_HOME_PATH is unset." >&2
  exit 1
fi
set -u

log "CANN_ROOT=$CANN_ROOT"
log "ASCEND_HOME_PATH=${ASCEND_HOME_PATH:-unset}"
if [[ -n "$CANN_REQUIRED_VERSION" ]]; then
  CANN_REAL="$(readlink -f "${ASCEND_HOME_PATH:-$CANN_ROOT}")"
  if [[ "$CANN_REAL" != *"$CANN_REQUIRED_VERSION"* ]]; then
    echo "Expected CANN $CANN_REQUIRED_VERSION, resolved: $CANN_REAL" >&2
    exit 1
  fi
fi

if [[ -z "$DEST" ]]; then
  for site_packages in \
    "$CANN_ROOT/python/site-packages" \
    "${ASCEND_HOME_PATH:-$CANN_ROOT}/python/site-packages" \
    "$(dirname "$CANN_ROOT")/ascend-toolkit/latest/python/site-packages"; do
    if [[ -d "$site_packages" ]]; then
      DEST="$site_packages/mooncake"
      break
    fi
  done
fi
if [[ -z "$DEST" ]]; then
  echo "Cannot locate CANN python/site-packages; set DEST explicitly." >&2
  exit 1
fi
log "Mooncake library destination=$DEST"

if [[ "${PROXY_IP:-}" == "none" ]]; then
  PROXY_IP=""
elif [[ -z "${PROXY_IP:-}" ]]; then
  SERVER_IPS="${TARGET_SERVER_IP:-$(hostname -I 2>/dev/null || true)}"
  case " $SERVER_IPS " in
    *" 141."*) PROXY_IP="141.4.152.201" ;;
    *" 80."*) PROXY_IP="80.254.137.250" ;;
    *" 90."*) PROXY_IP="90.254.35.230" ;;
    *)
      echo "Cannot select a proxy for server addresses: ${SERVER_IPS:-unknown}" >&2
      echo "Ask the user for the current proxy IP, then rerun with PROXY_IP=<ip>." >&2
      exit 1
      ;;
  esac
fi

if [[ -n "$PROXY_IP" ]]; then
  log "checking proxy http://${PROXY_IP}:${PROXY_PORT}"
  HTTP_CODE="$(curl -ksS -o /dev/null -w '%{http_code}' --connect-timeout 3 --max-time 8 \
    --proxy "http://${PROXY_IP}:${PROXY_PORT}" https://github.com/ || true)"
  if [[ "$HTTP_CODE" == "000" || -z "$HTTP_CODE" ]]; then
    echo "Proxy http://${PROXY_IP}:${PROXY_PORT} is unreachable." >&2
    echo "The user's local-computer IP may have changed; ask for the current proxy IP." >&2
    exit 1
  fi
  log "proxy reachable (HTTP ${HTTP_CODE})"
  export http_proxy="http://${PROXY_IP}:${PROXY_PORT}"
  export https_proxy="$http_proxy" HTTP_PROXY="$http_proxy" HTTPS_PROXY="$http_proxy"
else
  log "proxy disabled by PROXY_IP=none"
  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true
fi
export no_proxy="127.0.0.1,localhost,local,.local,*.huawei.com"
export NO_PROXY="$no_proxy"
export GIT_SSL_NO_VERIFY=true CMAKE_TLS_VERIFY=0
export GOTOOLCHAIN=local GOPROXY=https://goproxy.cn,https://goproxy.io,direct GOSUMDB=off
export PATH="/usr/local/go/bin:/usr/local/python3.11.10/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH:-}"

deps_ready() {
  command -v cmake >/dev/null 2>&1 &&
    command -v ninja >/dev/null 2>&1 &&
    command -v patchelf >/dev/null 2>&1 &&
    [[ -f /usr/lib64/cmake/gflags/gflags-config.cmake ]] &&
    [[ -f /usr/include/json/json.h ]] &&
    find /usr /usr/local -type f \
      \( -name 'yalantinglibsConfig.cmake' -o -name 'yalantinglibs-config.cmake' \) \
      -print -quit 2>/dev/null | grep -q .
}

if deps_ready; then
  log "required openEuler build dependencies are already present"
else
  log "openEuler system packages and source-pinned submodules"
  if [[ ! -f "${MOONCAKE_SRC}/scripts/ascend/dependencies_openeuler.sh" ]]; then
    echo "This checkout has no scripts/ascend/dependencies_openeuler.sh" >&2
    exit 1
  fi
  set +e
  bash "${MOONCAKE_SRC}/scripts/ascend/dependencies_openeuler.sh" -y
  DEPS_RC=$?
  set -e
  if [[ "$DEPS_RC" -ne 0 ]]; then
    log "dependency installer exited $DEPS_RC; checking required C/C++ postconditions"
  fi
fi

if [[ ! -f /usr/include/yaml-cpp/yaml.h ]]; then
  log "installing yaml-cpp-devel"
  if command -v dnf >/dev/null 2>&1; then
    dnf install -y yaml-cpp-devel
  else
    yum install -y yaml-cpp-devel
  fi
fi

if ! find /usr /usr/local -type f \
  \( -name 'yalantinglibsConfig.cmake' -o -name 'yalantinglibs-config.cmake' \) \
  -print -quit 2>/dev/null | grep -q .; then
  if [[ -f "${MOONCAKE_SRC}/extern/yalantinglibs/CMakeLists.txt" ]]; then
    YLT_SRC="${MOONCAKE_SRC}/extern/yalantinglibs"
  fi
  if [[ ! -f "$YLT_SRC/CMakeLists.txt" ]]; then
    echo "yalantinglibs is not installed and no source checkout was found." >&2
    echo "Initialize the source-pinned submodule or set YLT_SRC explicitly." >&2
    exit 1
  fi
  log "installing yalantinglibs from $YLT_SRC"
  rm -rf "$YLT_SRC/build"
  cmake -S "$YLT_SRC" -B "$YLT_SRC/build" \
    -DBUILD_EXAMPLES=OFF -DBUILD_BENCHMARK=OFF -DBUILD_UNIT_TESTS=OFF
  cmake --build "$YLT_SRC/build" -j"$(nproc)"
  cmake --install "$YLT_SRC/build"
fi

if ! deps_ready; then
  echo "Required C/C++ build dependencies are still incomplete." >&2
  exit 1
fi

if grep -Rqs --include='*.h' --include='*.hpp' --include='*.cc' --include='*.cpp' \
  'msgpack\.hpp' "$MOONCAKE_SRC" && [[ ! -f /usr/local/include/msgpack.hpp ]]; then
  log "installing msgpack-c cpp-7.0.0"
  if [[ ! -d "$MSGPACK_SRC" ]]; then
    git clone --depth 1 --branch cpp-7.0.0 \
      https://github.com/msgpack/msgpack-c.git "$MSGPACK_SRC"
  elif ! git -C "$MSGPACK_SRC" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "MSGPACK_SRC exists but is not a git checkout: $MSGPACK_SRC" >&2
    exit 1
  fi
  git -C "$MSGPACK_SRC" checkout cpp-7.0.0
  rm -rf "$MSGPACK_SRC/build"
  cmake -S "$MSGPACK_SRC" -B "$MSGPACK_SRC/build" \
    -DMSGPACK_USE_BOOST=OFF -DMSGPACK_BUILD_DOCS=OFF \
    -DMSGPACK_BUILD_EXAMPLES=OFF -DMSGPACK_BUILD_TESTS=OFF
  cmake --build "$MSGPACK_SRC/build" -j"$(nproc)"
  cmake --install "$MSGPACK_SRC/build"
fi

log "unversioned .so symlinks"
[[ -e /usr/lib64/libcurl.so ]]    || ln -sf libcurl.so.4    /usr/lib64/libcurl.so
[[ -e /usr/lib64/libhiredis.so ]] || ln -sf libhiredis.so.1 /usr/lib64/libhiredis.so
[[ -e /usr/lib64/libnuma.so ]]    || ln -sf libnuma.so.1    /usr/lib64/libnuma.so
ldconfig
test -f /usr/lib64/cmake/gflags/gflags-config.cmake
test -f /usr/include/json/json.h
test -e /usr/lib64/libjsoncpp.so

log "cmake + ninja"
if [[ "$CLEAN_BUILD" == "1" ]]; then
  rm -rf "${MOONCAKE_SRC}/build"
fi
mkdir -p "${MOONCAKE_SRC}/build"
cmake -S "$MOONCAKE_SRC" -B "${MOONCAKE_SRC}/build" -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DUSE_ASCEND_DIRECT=ON -DUSE_CUDA=OFF -DWITH_EP=OFF \
  -DBUILD_SHARED_LIBS=ON -DBUILD_UNIT_TESTS=OFF -DBUILD_EXAMPLES=OFF \
  -DUSE_HTTP=ON -DUSE_ETCD=OFF -DSTORE_USE_ETCD=OFF \
  -DWITH_STORE_RUST=OFF -DWITH_STORE_GO=OFF \
  -Dgflags_DIR=/usr/lib64/cmake/gflags \
  -DJSONCPP_INCLUDE_DIR=/usr/include \
  -DJSONCPP_LIBRARY=/usr/lib64/libjsoncpp.so \
  -DCMAKE_PREFIX_PATH="${ASCEND_HOME_PATH:-$CANN_ROOT};/usr;/usr/local" \
  -DCMAKE_TLS_VERIFY=0

cmake --build "${MOONCAKE_SRC}/build"
cmake --install "${MOONCAKE_SRC}/build"

log "copy .so into CANN python site-packages"
mkdir -p "$DEST"
cp -f \
  "$INSTALL_LIBDIR/libmooncake_common.so" \
  "$INSTALL_LIBDIR/libtransfer_engine.so" \
  "$INSTALL_LIBDIR/libmooncake_store.so" \
  "$DEST/"
ldconfig
ls -lh \
  "${DEST}/libmooncake_common.so" \
  "${DEST}/libtransfer_engine.so" \
  "${DEST}/libmooncake_store.so"

log "DONE"
