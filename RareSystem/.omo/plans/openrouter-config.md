# OpenRouter 配置计划

## TL;DR

> **快速摘要**: 配置 OpenRouter 作为 OpenCode 的模型提供商，支持 Claude、GPT 和 Gemini 等多种模型。
> 
> **交付物**:
> - 更新后的 `~/.config/opencode/opencode.json`
> - 配置好的 OpenRouter API 密钥
> - 更新后的 `oh-my-openagent.json` 代理模型配置

---

## 背景

用户已安装 oh-my-openagent，现在需要配置 OpenRouter 作为主要模型提供商。

---

## 工作目标

### 核心目标
配置 OpenRouter 提供商并更新代理模型映射。

### 具体交付物
- OpenRouter 提供商配置
- API 密钥认证
- 代理模型更新

---

## TODOs

- [ ] 1. 更新 OpenCode 配置文件

  **要做什么**:
  编辑 `~/.config/opencode/opencode.json`，添加 OpenRouter 提供商配置：
  
  ```json
  {
    "$schema": "https://opencode.ai/config.json",
    "autoupdate": true,
    "permission": {
      "edit": "ask",
      "bash": "ask",
      "file_write": "allow",
      "file_delete": "ask"
    },
    "formatter": true,
    "lsp": true,
    "plugin": [
      "oh-my-openagent"
    ],
    "provider": {
      "openrouter": {
        "models": {
          "anthropic/claude-opus-4": {
            "name": "Claude Opus 4"
          },
          "anthropic/claude-sonnet-4": {
            "name": "Claude Sonnet 4"
          },
          "anthropic/claude-haiku-4": {
            "name": "Claude Haiku 4"
          },
          "openai/gpt-4o": {
            "name": "GPT-4o"
          },
          "google/gemini-2.0-pro": {
            "name": "Gemini 2.0 Pro"
          }
        }
      }
    }
  }
  ```

  **验证**:
  - [ ] 文件内容正确更新
  - [ ] JSON 格式有效

- [ ] 2. 配置 OpenRouter API 密钥

  **要做什么**:
  在 OpenCode 中运行命令：
  ```
  /connect
  ```
  然后选择 OpenRouter 并输入 API 密钥。

  **验证**:
  - [ ] 密钥存储在 `~/.local/share/opencode/auth.json`
  - [ ] 运行 `/models` 可以看到 OpenRouter 模型列表

- [ ] 3. 更新 oh-my-openagent 代理模型配置

  **要做什么**:
  编辑 `~/.config/opencode/oh-my-openagent.json`，将代理模型更改为 OpenRouter：

  ```json
  {
    "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-opencode.schema.json",
    "agents": {
      "sisyphus": {
        "model": "openrouter/anthropic/claude-opus-4"
      },
      "prometheus": {
        "model": "openrouter/anthropic/claude-opus-4"
      },
      "oracle": {
        "model": "openrouter/openai/gpt-4o"
      },
      "hephaestus": {
        "model": "openrouter/openai/gpt-4o"
      },
      "explore": {
        "model": "openrouter/anthropic/claude-haiku-4"
      },
      "librarian": {
        "model": "openrouter/anthropic/claude-haiku-4"
      },
      "metis": {
        "model": "openrouter/anthropic/claude-sonnet-4"
      },
      "momus": {
        "model": "openrouter/openai/gpt-4o"
      },
      "atlas": {
        "model": "openrouter/anthropic/claude-sonnet-4"
      },
      "multimodal-looker": {
        "model": "openrouter/google/gemini-2.0-pro"
      },
      "sisyphus-junior": {
        "model": "openrouter/anthropic/claude-sonnet-4"
      }
    },
    "categories": {
      "visual-engineering": {
        "model": "openrouter/anthropic/claude-sonnet-4"
      },
      "ultrabrain": {
        "model": "openrouter/anthropic/claude-opus-4"
      },
      "deep": {
        "model": "openrouter/anthropic/claude-opus-4"
      },
      "artistry": {
        "model": "openrouter/anthropic/claude-sonnet-4"
      },
      "quick": {
        "model": "openrouter/anthropic/claude-haiku-4"
      },
      "unspecified-low": {
        "model": "openrouter/anthropic/claude-haiku-4"
      },
      "unspecified-high": {
        "model": "openrouter/anthropic/claude-sonnet-4"
      },
      "writing": {
        "model": "openrouter/anthropic/claude-sonnet-4"
      }
    }
  }
  ```

  **验证**:
  - [ ] 文件内容正确更新
  - [ ] JSON 格式有效

---

## 成功标准

- [ ] OpenRouter 提供商已配置
- [ ] API 密钥已存储
- [ ] 所有代理使用 OpenRouter 模型
- [ ] 运行 `opencode` 可以正常使用
