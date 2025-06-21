import os
import time
import asyncio
from typing import Any, AsyncGenerator, Optional

from litellm import acompletion, completion
from litellm.types.utils import ModelResponse

import streamlit as st
from src.setting import env_setting as setting
from streamlit.delta_generator import DeltaGenerator

# Create a client object
os.environ["OPENAI_API_KEY"] = setting.OPENAI_API_KEY

# サポートされていないパラメータを削除
import litellm

litellm.drop_params = True

# 無限ループ防止が厳しすぎるので、デフォルトを上げる
litellm.REPEATED_STREAMING_CHUNK_LIMIT = 10000


def completion_with_retry(model: str, **kwargs: Any) -> Any:
    """
    リトライ回数を設定したcompletion関数
    """
    for _i in range(5):
        try:
            return completion(model=model, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(15)
    return completion(model=model, **kwargs)


async def acompletion_with_retry(model: str, **kwargs: Any) -> Any:
    """
    リトライ回数を設定したacompletion関数
    """
    for _ in range(5):
        try:
            return await acompletion(model=model, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(15)
    return await acompletion(model=model, **kwargs)


def generate_stream(
    messages: list[dict[str, str]] | str,
    model: str = "gpt-4.1",
    temperature: float = 0,
    max_tokens: Optional[int] = None,
    system: str = "",
    result_area: Optional[DeltaGenerator] = None,
    suppress_output: bool = False,
    seed: int = 42,
) -> str:
    messages = convert_messages(messages)
    if system != "":
        messages.insert(0, {"role": "system", "content": system})

    if result_area is None:
        result_area = st.empty()
    if model.startswith("claude-3-5-sonnet"):
        max_tokens = 8192
    stream = support_streaming(model)
    resp = completion_with_retry(
        model=model,
        messages=messages,
        temperature=configure_temperture(temperature=temperature, model=model),
        max_tokens=max_tokens,
        stream=stream,
        seed=seed,
        num_retries=5,
    )
    result = ""
    cursor = "|"
    if stream:
        for part in resp:
            content = part.choices[0].delta.content or ""
            result += content
            if not suppress_output:
                result_area.write(result + cursor)
    else:
        part = resp
        content = part.choices[0].message.content or ""
        result += content
    if not suppress_output:
        result_area.write(result)
    return result


async def async_generate_stream(
    messages: list[dict[str, str]],
    model: str = "gpt-4.1",
    temperature: float = 0,
    max_tokens: int | None = None,
    system: str = "",
    result_area: DeltaGenerator = None,
    suppress_output: bool = False,
    seed: int = 42,
) -> str:
    messages = convert_messages(messages)
    if system != "":
        messages.insert(0, {"role": "system", "content": system})
    if not suppress_output:
        if result_area is None:
            result_area = st.empty()
    if model.startswith("claude-3-5-sonnet"):
        max_tokens = 8192

    stream = support_streaming(model)
    resp = await acompletion_with_retry(
        model=model,
        messages=messages,
        temperature=configure_temperture(temperature=temperature, model=model),
        max_tokens=max_tokens,
        stream=stream,
        seed=seed,
        num_retries=5,
    )
    return await _handle_response(resp, result_area, suppress_output, stream)


async def _handle_response(
    resp: AsyncGenerator[ModelResponse, None] | ModelResponse,
    result_area: Optional[DeltaGenerator],
    suppress_output: bool,
    stream: bool,
) -> str:
    result = ""
    if stream:
        async for part in resp:  # type: ignore
            content = part.choices[0].delta.content or ""  # type: ignore
            result += content
            if not suppress_output and result_area is not None:
                result_area.write(result)
            if part.choices[0].finish_reason == "length":
                break
    else:
        part = resp
        content = part.choices[0].message.content or ""  # type: ignore
        result += content
        if not suppress_output and result_area is not None:
            result_area.write(result)
    return result


def convert_messages(messages: list[Any] | list[dict[str, str]] | str) -> list[dict[str, str]]:
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    return messages


def support_streaming(model: str) -> bool:
    return "o1" not in model


def configure_temperture(temperature: int | float, model: str) -> float:
    is_o1_or_o3_family = "o1" in model or "o3" in model
    if is_o1_or_o3_family:
        return max(1, temperature)
    return temperature


def available_models():
    models = []
    if setting.OPENAI_API_KEY:
        models.extend(["gpt-4o", "gpt-4o-mini", "o1-mini", "o1-preview", "o1", "o3-mini"])
    return models
