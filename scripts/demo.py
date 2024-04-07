import lark_oapi as lark

# 创建client
client = lark.Client.builder().app_id("cli_a680e4c8c5be100c").app_secret("uKEDeCAamlviajfBrxXjBhiSKnxONf6x").build()

# 构造请求对象
request = lark.contact.v3.Spreadsheets.builder().user_id("15c2b353").build()

# 发起请求
response = client.contact.v3.user.get(request)
print(response.msg)
