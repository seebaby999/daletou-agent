#!/usr/bin/env python3
"""
大乐透选号生成器
纯随机或数学滤网模式，输出指定注数。
"""

import argparse
import random
import sys
from itertools import combinations
from typing import List, Tuple

# 全组合太大，不能枚举。使用拒绝采样 + 滤网。

FRONT = list(range(1, 36))
BACK = list(range(1, 13))


def is_valid_front(nums: List[int]) -> bool:
    """滤网：奇偶、大小、和值、跨度"""
    odds = sum(1 for n in nums if n % 2 == 1)
    if odds not in (2, 3):
        return False
    small = sum(1 for n in nums if n <= 17)
    if small not in (2, 3):
        return False
    s = sum(nums)
    if not (70 <= s <= 120):
        return False
    span = max(nums) - min(nums)
    if not (15 <= span <= 30):
        return False
    # 区间覆盖
    zones = [0, 0, 0]
    for n in nums:
        if n <= 12:
            zones[0] += 1
        elif n <= 24:
            zones[1] += 1
        else:
            zones[2] += 1
    if max(zones) >= 4:  # 过度集中
        return False
    return True


def is_valid_back(nums: List[int]) -> bool:
    odds = sum(1 for n in nums if n % 2 == 1)
    if odds not in (0, 1, 2):  # 宽松，优先1
        pass
    s = sum(nums)
    if not (6 <= s <= 20):
        return False
    span = max(nums) - min(nums)
    if span < 2:
        return False
    return True


def sample_front(rng: random.Random, use_filter: bool) -> List[int]:
    for _ in range(10000):
        nums = sorted(rng.sample(FRONT, 5))
        if not use_filter or is_valid_front(nums):
            return nums
    # fallback
    return sorted(rng.sample(FRONT, 5))


def sample_back(rng: random.Random, use_filter: bool) -> List[int]:
    for _ in range(1000):
        nums = sorted(rng.sample(BACK, 2))
        if not use_filter or is_valid_back(nums):
            return nums
    return sorted(rng.sample(BACK, 2))


def generate(count: int = 2, mode: str = "random", seed: int = None) -> List[Tuple[List[int], List[int]]]:
    rng = random.Random(seed)
    use_filter = mode == "filter"
    results = []
    seen = set()
    while len(results) < count:
        front = sample_front(rng, use_filter)
        back = sample_back(rng, use_filter)
        key = (tuple(front), tuple(back))
        if key not in seen:
            seen.add(key)
            results.append((front, back))
    return results


def main():
    parser = argparse.ArgumentParser(description="大乐透选号生成器")
    parser.add_argument("--mode", choices=["random", "filter"], default="random")
    parser.add_argument("--count", type=int, default=2)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    tickets = generate(args.count, args.mode, args.seed)
    print(f"模式: {args.mode} | 注数: {args.count}")
    print("-" * 40)
    for i, (front, back) in enumerate(tickets, 1):
        odds = sum(1 for n in front if n % 2 == 1)
        s = sum(front)
        span = max(front) - min(front)
        print(f"第{i}注: 前区 {' '.join(f'{n:02d}' for n in front)}  后区 {' '.join(f'{n:02d}' for n in back)}")
        print(f"       奇偶 {odds}:{5-odds}  和值 {s}  跨度 {span}")
    print("-" * 40)
    print("提醒: 大乐透一等奖概率 1/21,425,712。本工具不提高中奖率，仅供娱乐。请理性购彩。")


if __name__ == "__main__":
    main()
