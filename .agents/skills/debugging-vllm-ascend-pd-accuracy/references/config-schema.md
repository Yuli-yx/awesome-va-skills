# 配置格式

Skill 使用两个运行时文件：inventory 描述 SSH/容器/endpoint，case 描述请求和实验；两者都不应提交真实密码。

## inventory.example.yaml

```yaml
container: pd_kimi_zyx
ssh:
  connect_timeout: 10
  command_timeout: 60
  known_hosts_policy: auto_add
hosts:
  - name: decode-0
    host: 192.0.2.10
    user: root
    password_env: PD_SSH_PASSWORD_DECODE
    role: decode
    endpoint: http://192.0.2.10:1999
  - name: prefill-0
    host: 192.0.2.20
    user: root
    password_env: PD_SSH_PASSWORD_PREFILL
    role: prefill
    endpoint: http://192.0.2.20:1999
proxy:
  url: http://192.0.2.30:1999
```

`role` 可以省略；运行时优先从 `--kv-transfer-config` 自动识别。`password_env` 只保存环境变量名。也支持 `key_file`，优先使用 SSH key。

## case.example.yaml

```yaml
name: kimi-full-model-pd-repetition
request:
  method: POST
  path: /v1/completions
  headers:
    Content-Type: application/json
  json:
    model: kimi-k3
    prompt: "固定测试 prompt"
    temperature: 0
    max_tokens: 100
  repeats: 3
endpoints:
  - name: proxy
    url: http://192.0.2.30:1999
  - name: decode-0
    url: http://192.0.2.10:1999
experiments:
  readiness_timeout_seconds: 900
  per_experiment_timeout_seconds: 1800
  allow_container_restart: true
  enable_kv_fingerprint: auto
```

不要在 case 中保存 `Authorization` token；运行时通过 `PD_AUTH_TOKEN` 注入，脚本只在内存中添加请求头。
