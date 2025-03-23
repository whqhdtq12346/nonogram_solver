import random

r, c, n = map(int, input().split())

def get_hint(line):
    hint = []
    count = 0
    for entry in line:
        if entry == 1:
            count += 1
        elif count > 0:
            hint.append(count)
            count = 0
    if count > 0: hint.append(count)
    return hint if len(hint) > 0 else [0]

with open('nonogram_problems.txt', 'w') as file:
    for _ in range(n):
        answer = [[random.choice([-1, 1]) for _ in range(c)] for _ in range(r)]
        rows = [get_hint(row) for row in answer]
        cols = [get_hint(col) for col in zip(*answer)]
        
        for hint in rows:
            file.write('[')
            for i, num in enumerate(hint):
                if i < len(hint) - 1:
                    file.write(f"{num}, ")
                else:
                    file.write(f"{num}")
            file.write(']')
        file.write('\n')
        
        for hint in cols:
            file.write('[')
            for i, num in enumerate(hint):
                if i < len(hint) - 1:
                    file.write(f"{num}, ")
                else:
                    file.write(f"{num}")
            file.write(']')
        file.write('\n')
        
        for row in answer:
            file.write('[')
            for i, entry in enumerate(row):
                if i < len(row) - 1:
                    file.write(f"{entry}, ")
                else:
                    file.write(f"{entry}")
            file.write(']')
        file.write('\n')