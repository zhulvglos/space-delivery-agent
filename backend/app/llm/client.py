"""LLM 大模型客户端模块"""
from typing import Optional, List
from app.config import settings
import logging
import httpx
import asyncio
import json
import os
import shutil
import tempfile

try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - 允许只使用 Anthropic HTTP 客户端
    ChatOpenAI = None

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM 客户端封装类"""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.client = self._create_client()

    def _create_client(self):
        if not self.is_configured():
            return None
        if self.provider == "anthropic":
            return None
        if ChatOpenAI is None:
            raise RuntimeError("使用 openai/deepseek/qwen provider 需要安装 langchain-openai")
        if self.provider == "openai":
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                temperature=0.7,
                max_tokens=2000,
            )
        elif self.provider == "deepseek":
            return ChatOpenAI(
                model=settings.DEEPSEEK_MODEL,
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=0.7,
                max_tokens=2000,
            )
        elif self.provider == "qwen":
            return ChatOpenAI(
                model=settings.QWEN_MODEL,
                api_key=settings.QWEN_API_KEY,
                base_url=settings.QWEN_BASE_URL,
                temperature=0.7,
                max_tokens=2000,
            )
        else:
            raise ValueError(f"不支持的 LLM 提供商: {self.provider}")

    def is_configured(self) -> bool:
        if self.provider == "anthropic":
            return bool(settings.ANTHROPIC_API_KEY)
        if self.provider == "openai":
            return bool(settings.OPENAI_API_KEY)
        if self.provider == "deepseek":
            return bool(settings.DEEPSEEK_API_KEY)
        if self.provider == "qwen":
            return bool(settings.QWEN_API_KEY)
        return False

    async def acomplete(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成一段文本。支持 OpenAI-compatible 与 Anthropic Messages API。"""
        if not self.is_configured():
            raise RuntimeError(f"LLM_PROVIDER={self.provider} 未配置 API Key")

        try:
            if self.provider == "anthropic":
                return await self._acomplete_anthropic(prompt, system_prompt)
            return await self._acomplete_openai_compat(prompt, system_prompt)
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise

    async def _acomplete_openai_compat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """OpenAI-compatible 接口（openai / deepseek / qwen / siliconflow）。"""
        base_url = settings.OPENAI_BASE_URL.rstrip("/")
        url = f"{base_url}/chat/completions"
        headers = {"content-type": "application/json", "Authorization": f"Bearer {settings.OPENAI_API_KEY or ''}"}
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 400,
        }
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS, verify=ctx, trust_env=False) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
        choices = data.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""

    async def _acomplete_anthropic(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        base_url = settings.ANTHROPIC_BASE_URL.rstrip("/")
        url = f"{base_url}/v1/messages"
        headers = {
            "content-type": "application/json",
            "x-api-key": settings.ANTHROPIC_API_KEY or "",
            "authorization": f"Bearer {settings.ANTHROPIC_API_KEY or ''}",
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": settings.ANTHROPIC_MODEL,
            "max_tokens": 400,
            "temperature": 0.4,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS, verify=ctx, trust_env=False) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.RemoteProtocolError, httpx.ReadError) as exc:
            logger.warning("Python HTTP 客户端连接 Anthropic 代理失败，尝试 curl 原始字节传输兜底: %r", exc)
            try:
                data = await self._acomplete_anthropic_via_curl(url, payload)
            except Exception as curl_exc:
                logger.warning("curl Anthropic 调用失败，尝试 PowerShell 传输兜底: %r", curl_exc)
                data = await self._acomplete_anthropic_via_powershell(url, payload)

        content = data.get("content", [])
        if isinstance(content, list):
            # 优先取 text 块，若无则取 thinking 块（mimo/extended-thinking 模型）
            texts = [part.get("text", "") for part in content if part.get("type") == "text"]
            if not texts:
                texts = [part.get("thinking", "") for part in content if part.get("type") == "thinking"]
            return "".join(texts)
        return str(content)

    async def _acomplete_anthropic_via_curl(self, url: str, payload: dict) -> dict:
        """Use curl.exe on Windows to preserve UTF-8 response bytes from the proxy."""
        curl_path = shutil.which("curl.exe") or shutil.which("curl")
        if not curl_path:
            raise RuntimeError("未找到 curl.exe")

        payload_path = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as payload_file:
                payload_path = payload_file.name
                json.dump(payload, payload_file, ensure_ascii=False)

            process = await asyncio.create_subprocess_exec(
                curl_path,
                "-sS",
                "-X",
                "POST",
                url,
                "-H",
                "content-type: application/json; charset=utf-8",
                "-H",
                f"x-api-key: {settings.ANTHROPIC_API_KEY or ''}",
                "-H",
                f"authorization: Bearer {settings.ANTHROPIC_API_KEY or ''}",
                "-H",
                "anthropic-version: 2023-06-01",
                "--max-time",
                str(settings.LLM_TIMEOUT_SECONDS),
                "--data-binary",
                f"@{payload_path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            output = stdout.decode("utf-8", errors="replace").strip()
            error = stderr.decode("utf-8", errors="replace").strip()
            if process.returncode != 0:
                raise RuntimeError(f"curl Anthropic 调用失败: {error or output}")
            if not output:
                raise RuntimeError(f"curl Anthropic 调用没有输出。stderr={error[:500]}")
            data = json.loads(output)
            if data.get("error"):
                raise RuntimeError(f"curl Anthropic API 错误: {data['error']}")
            return data
        finally:
            if payload_path:
                try:
                    os.remove(payload_path)
                except OSError:
                    pass

    async def _acomplete_anthropic_via_powershell(self, url: str, payload: dict) -> dict:
        """Windows/Anaconda HTTPS 异常时，用 PowerShell 原生网络栈兜底。"""
        if os.name != "nt":
            raise RuntimeError("PowerShell Anthropic 兜底仅支持 Windows")

        script = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$body = Get-Content -Path $env:ANTHROPIC_PAYLOAD_PATH -Raw -Encoding UTF8
$headers = @{
  'x-api-key' = $env:ANTHROPIC_API_KEY
  'authorization' = 'Bearer ' + $env:ANTHROPIC_API_KEY
  'anthropic-version' = '2023-06-01'
}
$res = Invoke-RestMethod -Uri $env:ANTHROPIC_URL -Method Post -Headers $headers -Body $body -ContentType 'application/json; charset=utf-8' -TimeoutSec $env:LLM_TIMEOUT_SECONDS
$res | ConvertTo-Json -Depth 20 -Compress
"""
        env = os.environ.copy()
        env["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY or ""
        env["ANTHROPIC_URL"] = url
        env["LLM_TIMEOUT_SECONDS"] = str(settings.LLM_TIMEOUT_SECONDS)
        payload_path = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as payload_file:
                payload_path = payload_file.name
                json.dump(payload, payload_file, ensure_ascii=False)
            env["ANTHROPIC_PAYLOAD_PATH"] = payload_path
            process = await asyncio.create_subprocess_exec(
                "powershell",
                "-NoProfile",
                "-Command",
                script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            stdout, stderr = await process.communicate()
            output = stdout.decode("utf-8", errors="replace").strip()
            error = stderr.decode("utf-8", errors="replace").strip()
            if process.returncode != 0:
                raise RuntimeError(f"PowerShell Anthropic 调用失败: {error or output}")
            if not output:
                raise RuntimeError(f"PowerShell Anthropic 调用没有输出。stderr={error[:500]}")
            return json.loads(output)
        finally:
            if payload_path:
                try:
                    os.remove(payload_path)
                except OSError:
                    pass

    async def agenerate(self, prompts: List[str]):
        try:
            from langchain.schema import HumanMessage
            messages = [HumanMessage(content=prompt) for prompt in prompts]
            response = await self.client.agenerate(messages)
            return response
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise


_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
