from __future__ import annotations

import json
import re
from typing import Iterable

from .models import Failure, StackFrame

FAILURE_START_RE = re.compile(r"^---\s+([^\s:]+)(?:::(.+))?$")
STACK_FRAME_RE = re.compile(
    r"^\s*at\s+([A-Za-z0-9_.$<>]+)\.([A-Za-z0-9_$<>]+)\(([^:()]+)?(?::(\d+))?\)\s*$"
)


def parse_failing_tests(contents: str) -> list[Failure]:
    failures: list[Failure] = []
    current_name: str | None = None
    current_lines: list[str] = []
    for raw_line in contents.splitlines():
        match = FAILURE_START_RE.match(raw_line.strip())
        if match:
            if current_name is not None:
                failures.append(_build_failure(current_name, current_lines))
            test_class = match.group(1)
            method = match.group(2)
            current_name = f"{test_class}::{method}" if method else test_class
            current_lines = []
            continue
        if current_name is not None:
            current_lines.append(raw_line.rstrip("\n"))
    if current_name is not None:
        failures.append(_build_failure(current_name, current_lines))
    return failures


def parse_failing_tests_from_output(output: str) -> list[Failure]:
    return parse_failing_tests(output)


def _build_failure(test_name: str, lines: list[str]) -> Failure:
    if "::" in test_name:
        test_class, test_method = test_name.split("::", 1)
    else:
        test_class, test_method = test_name, None
    headline = None
    for line in lines:
        stripped = line.strip()
        if stripped:
            headline = stripped
            break
    frames = parse_stack_frames(lines)
    return Failure(
        test_name=test_name,
        test_class=test_class,
        test_method=test_method,
        headline=headline,
        stack_trace=list(lines),
        frames=frames,
    )


def parse_stack_frames(lines: Iterable[str]) -> list[StackFrame]:
    frames: list[StackFrame] = []
    for line in lines:
        match = STACK_FRAME_RE.match(line)
        if not match:
            continue
        file_name = match.group(3)
        line_number = int(match.group(4)) if match.group(4) else None
        frames.append(
            StackFrame(
                class_name=match.group(1),
                method_name=match.group(2),
                file_name=file_name,
                line_number=line_number,
                raw=line.strip(),
            )
        )
    return frames


def extract_json_object(text: str) -> dict:
    text = text.strip()
    if not text:
        raise ValueError("LLM response was empty.")
    decoder = json.JSONDecoder()
    candidates = [text]
    if "```" in text:
        candidates.extend(_code_block_candidates(text))
    for candidate in candidates:
        candidate = candidate.strip()
        if not candidate:
            continue
        try:
            obj, index = decoder.raw_decode(candidate)
        except json.JSONDecodeError:
            brace_index = candidate.find("{")
            if brace_index >= 0:
                try:
                    obj, index = decoder.raw_decode(candidate[brace_index:])
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    return obj
            continue
        if index and isinstance(obj, dict):
            return obj
    raise ValueError("Could not parse a JSON object from the LLM response.")


def _code_block_candidates(text: str) -> list[str]:
    blocks: list[str] = []
    parts = text.split("```")
    for idx in range(1, len(parts), 2):
        block = parts[idx]
        if "\n" in block:
            _, remainder = block.split("\n", 1)
            blocks.append(remainder)
        else:
            blocks.append(block)
    return blocks
