import sys
sys.stdin = open("input.txt", "r")
sys.stdout = open("output.txt", "w")

def simulate(times, stair_len):
    # times: 이 계단을 이용하는 사람들의 "계단 입구 도착 후 입장 가능 시간"
    if not times:
        return 0

    times.sort()    
    finish = []

    for i in range(len(times)):
        if i < 3:
            start = times[i]
        else:
            start = max(times[i], finish[i - 3])

        finish.append(start + stair_len)

    return finish[-1]


def dfs(idx):
    global answer

    if idx == len(people):
        stair1_times = []
        stair2_times = []

        for i in range(len(people)):
            pr, pc = people[i]
            if selected[i] == 0:
                sr, sc, slen = stairs[0]
                stair1_times.append(abs(pr - sr) + abs(pc - sc) + 1)
            else:
                sr, sc, slen = stairs[1]
                stair2_times.append(abs(pr - sr) + abs(pc - sc) + 1)

        time1 = simulate(stair1_times, stairs[0][2])
        time2 = simulate(stair2_times, stairs[1][2])

        answer = min(answer, max(time1, time2))
        return

    selected[idx] = 0
    dfs(idx + 1)

    selected[idx] = 1
    dfs(idx + 1)


T = int(input())
for tc in range(1, T + 1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]

    people = []
    stairs = []

    for i in range(N):
        for j in range(N):
            if arr[i][j] == 1:
                people.append((i, j))
            elif arr[i][j] > 1:
                stairs.append((i, j, arr[i][j]))  # r, c, 길이

    selected = [0] * len(people)
    answer = float('inf')

    dfs(0)

    print(f"#{tc} {answer}")