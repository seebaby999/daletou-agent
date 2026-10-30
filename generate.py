#!/usr/bin/env python3
"""大乐透二柱，种子锁定 2026-10-31。与网页同一算法。"""

import argparse

TARGET = "2026-10-31"
FRONT = list(range(1, 36))
BACK = list(range(1, 13))


def i32(n: int) -> int:
    n &= 0xFFFFFFFF
    if n & 0x80000000:
        n -= 0x100000000
    return n


def u32(n: int) -> int:
    return n & 0xFFFFFFFF


def imul(a: int, b: int) -> int:
    return i32(i32(a) * i32(b))


def hash_string(s: str) -> int:
    h = 2166136261
    for ch in s:
        h = u32(h) ^ ord(ch)
        h = u32(imul(h, 16777619))
    return u32(h)


def mulberry32(seed: int):
    a = seed & 0xFFFFFFFF

    def rng() -> float:
        nonlocal a
        a = i32(a)
        a = i32(a + 0x6D2B79F5)
        t = imul(i32(i32(a) ^ (u32(a) >> 15)), i32(1 | i32(a)))
        t = i32(i32(t + imul(i32(i32(t) ^ (u32(t) >> 7)), i32(61 | i32(t)))) ^ i32(t))
        return u32(i32(t) ^ (u32(t) >> 14)) / 4294967296

    return rng


def sample(pool, k, rng):
    bag = pool[:]
    for i in range(len(bag) - 1, 0, -1):
        j = int(rng() * (i + 1))
        bag[i], bag[j] = bag[j], bag[i]
    return sorted(bag[:k])


def valid_front(nums):
    odds = sum(n % 2 for n in nums)
    if odds not in (2, 3):
        return False
    small = sum(n <= 17 for n in nums)
    if small not in (2, 3):
        return False
    total = sum(nums)
    if not 70 <= total <= 120:
        return False
    span = max(nums) - min(nums)
    if not 15 <= span <= 30:
        return False
    zones = [0, 0, 0]
    for n in nums:
        if n <= 12:
            zones[0] += 1
        elif n <= 24:
            zones[1] += 1
        else:
            zones[2] += 1
    return max(zones) < 4


def valid_back(nums):
    total = sum(nums)
    if not 6 <= total <= 20:
        return False
    return max(nums) - min(nums) >= 2


def generate(mode: str, salt: int):
    rng = mulberry32(hash_string(f"{TARGET}|{mode}|{salt}"))
    use_filter = mode == "filter"
    out = []
    seen = set()
    guard = 0
    while len(out) < 2 and guard < 20000:
        guard += 1
        front = sample(FRONT, 5, rng)
        back = sample(BACK, 2, rng)
        if use_filter:
            tries = 0
            while not valid_front(front) and tries < 400:
                front = sample(FRONT, 5, rng)
                tries += 1
            tries = 0
            while not valid_back(back) and tries < 80:
                back = sample(BACK, 2, rng)
                tries += 1
        key = f"{front}|{back}"
        if key in seen:
            continue
        seen.add(key)
        out.append((front, back))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["filter", "random"], default="filter")
    p.add_argument("--salt", type=int, default=0)
    args = p.parse_args()
    print(f"指向 {TARGET} 周六 | {args.mode} | #{args.salt}")
    for i, (front, back) in enumerate(generate(args.mode, args.salt), 1):
        odds = sum(n % 2 for n in front)
        print(
            f"第{i}注 前区 {' '.join(f'{n:02d}' for n in front)}  "
            f"后区 {' '.join(f'{n:02d}' for n in back)}  "
            f"奇偶 {odds}:{5 - odds} 和值 {sum(front)} 跨度 {max(front) - min(front)}"
        )
    print("一等奖单注 1/21425712。种子只锁定本期可复现，不提高概率。")


if __name__ == "__main__":
    main()
