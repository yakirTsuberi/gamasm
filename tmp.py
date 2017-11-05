import requests
import jwt

baseurl = 'http://127.0.0.1:5000/api'
print(requests.post(baseurl + '/auth', data={'email': 'yakir@ravtech.co.il',
                                                   'pw': '1q2w3e4r'}).text)
# SECRET = '>Nv}mH^23P-P3U:_e[^m]Wj+v<(T6TH!'
# #
# a = jwt.decode('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZW1haWwiOiJ5YWtpckByYXZ0ZWNoLmNvLmlsIn0._sfM9H8kpP84kVWu8cMRduLPy1mEWGp3Ed46pJA0ykQ'.encode(), SECRET)
#
# print(a)
print(requests.get(baseurl + '/my_sale', headers={'Authentication': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZW1haWwiOiJ5YWtpckByYXZ0ZWNoLmNvLmlsIn0._sfM9H8kpP84kVWu8cMRduLPy1mEWGp3Ed46pJA0ykQ'}).json())
