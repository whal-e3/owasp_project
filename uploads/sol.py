#!/usr/bin/env python3

result = "C@qpl==Bppl@<=pG<>@l>@Blsp<@l@AArqmGr=B@A>q@@B=GEsmC@ArBmAGlA=@q"
result2 = ""
for i in range(len(result)):
	result2 += chr(ord(result[i]) ^ 3)


res3 = ""
for i in range(len(result2)-1,-1,-1):
	res3 += result2[i]
print("res3: ", res3)

key = ""
for i in range(len(res3)):
	for k in range(1, 0x7f):
		if ((k+13) & 0x7f) == ord(res3[i]):
			print(k)
			key += chr(k)
			break
print("key: ", key)