# Mooncake compile — extra notes

Keep SKILL.md as the runbook. Use this only when a step fails.

## OS

Target is **openEuler 24.03 SP4 aarch64** (RPM, libs in `/usr/lib64`). Ubuntu/Debian multiarch instructions from upstream blogs do not apply.

## CANN mix-up from one prior environment

| Tree | Version | Role |
| --- | --- | --- |
| `/opt/cann-selected` | 9.2.0 | Selected for that build |
| `/usr/local/Ascend` | 9.1.0 + driver 25.6.rc1 | A different install that was not selected |

This table is evidence from one container, not a global path rule. On every target, inspect the user-provided `CANN_ROOT`, resolve its symlinks, source only that installation's `set_env.sh`, and confirm the resulting `ASCEND_HOME_PATH`. A standalone CANN root may contain `set_env.sh` and `python/site-packages` directly; a bundle root may contain `cann/set_env.sh` and `ascend-toolkit/set_env.sh`.

## Corporate TLS

Issuer `Huawei Web Secure Internet Gateway CA V2` can break curl/cmake/go (HTTP 60 / x509 unknown authority). In that environment, `GIT_SSL_NO_VERIFY=true`, `CMAKE_TLS_VERIFY=0`, and `GOSUMDB=off` were needed.

Prefer the `yalantinglibs` revision pinned by the current Mooncake checkout's submodule. An older checkout used commit `7801bc9ad9021781f15217552214e325a1cf7373`; do not apply that pin to newer revisions without checking their source metadata.

## ETCD / Go

`go.mod` may request toolchain go1.25.10 while the image has `/usr/local/go` 1.25.9. Downloading the toolchain fails TLS. The three `.so` files do not need etcd. Keep `-DUSE_ETCD=OFF -DSTORE_USE_ETCD=OFF -DWITH_STORE_GO=OFF`.

If the user insists on etcd: install a matching Go, `export GOTOOLCHAIN=local`, trust the gateway CA, then reconfigure.

Some openEuler dependency installers always download a fixed Go version even when the intended Mooncake configuration disables ETCD and store Go. If that final optional download fails after the required packages, submodules, and `yalantinglibs` installation have succeeded, check the C/C++ postconditions and proceed without Go. Do not use this exception when ETCD or Go-backed store support is enabled.

## rpm says installed, files missing

Container overlay often has gflags/glog/jsoncpp in the rpm DB but no unversioned `.so` or cmake file. `yum reinstall` may still not appear if `/usr/lib64` is a bind-mount. Creating the three symlinks in SKILL.md is the proven fix. jsoncpp headers live at `/usr/include/json/json.h` (not `jsoncpp/json/json.h`).

## Older msgpack helper false success

Some older `scripts/ascend/dependencies_ascend_installation.sh` revisions use `set +e`. yaml-cpp installation can succeed while msgpack CMake dies on CMP0167. Check whether the current Mooncake revision actually requires `msgpack.hpp`; if it does, verify the header before configuring.

## Build-tree versus install-tree libraries

After `cmake --install`, copy the libraries from the configured install libdir (commonly `/usr/local/lib`) into the CANN Python package. Raw build-tree libraries can contain absolute RPATH entries pointing back into `Mooncake/build`, making the installed package depend on a disposable build directory.

## vLLM after install

Mooncake compile success does **not** mean `vllm serve` will start. A typical follow-on error is `Package_Error_Verify_Package(E30009)` on `cann-hybm-compat.tar.gz` / unsigned `cann-hixl-compat.tar.gz` vs Huawei-mode driver 25.6 on 950. That is device package signature, not a missing Mooncake `.so`.

## Import succeeds, process aborts on exit

If `import mooncake.engine`, `import mooncake.store`, or `ctypes.CDLL(libtransfer_engine.so)` prints its success marker and then exits with `corrupted size vs. prev_size` / code 134, distinguish this from a loader failure: the extension loaded, but a native unload/destructor path corrupted heap state. Confirm that `ldd` has no `not found`, CANN libraries come from the selected tree, and package libraries do not contain build-tree RPATHs. Report the runtime failure explicitly; do not relabel it as a compile or missing-library failure, and do not claim end-to-end runtime validation.
