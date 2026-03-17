import sys
sys.stdin = open("input.txt", "r")
sys.stdout = open("output.txt", "w")

def calc(food):
    total = 0
    for i in range(len(food)):
        for j in range(i + 1, len(food)):
            a = food[i]
            b = food[j]
            total += ingredient[a][b] + ingredient[b][a]
    return total


def dfs(start, picked):
    global answer

    if len(picked) == N // 2:
        other = []
        for x in range(N):
            if x not in picked:
                other.append(x)

        taste1 = calc(picked)
        taste2 = calc(other)

        answer = min(answer, abs(taste1 - taste2))
        return

    for i in range(start, N):
        picked.append(i)
        dfs(i + 1, picked)
        picked.pop()


T = int(input())
for test_case in range(1, T + 1):
    N = int(input())
    ingredient = [list(map(int, input().split())) for _ in range(N)]

    answer = float('inf')
    dfs(0, [])

    print(f"#{test_case} {answer}")

