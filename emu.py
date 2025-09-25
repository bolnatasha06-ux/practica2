import shlex
while True:
    a = input("vfs@ ")
    b = shlex.split(a)
    if a == "exit":
        break
    if len(b) == 0:
        continue
    if b[0] == "ls":
        print(b)
    elif b[0] == "cd":
        print(b)
    else:
        print(f'{b[0]}: command not found')

