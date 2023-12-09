n, k, p = map(int, input().split())
a = list(map(int, input().split()))
ans = 0
for i in range(n):
    for j in range(i + 1, n):
        ans += (a[i] * a[j] * (a[i] ** 3 + a[j] ** 3)) % p != k
print(ans)