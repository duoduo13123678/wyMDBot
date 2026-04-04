import requests
import json

BOT_ROOT = "http://127.0.0.1:3000"
BOT_TOKEN = "YOUR_TOKEN_HERE"

group_id = input("输入群号：")
folder_name = input("输入文件夹名：")
get_type = input("是获取根目录还是子目录下的文件夹？(y=根目录，n=子目录)")
if get_type == "y":
    filelist = requests.post(BOT_ROOT+f"/get_group_root_files?access_token={BOT_TOKEN}",data=json.dumps(
        {
            "group_id": int(group_id)
        }
    )).json()
    folders = filelist["data"]["folders"]
    for i in folders:
        if i["folder_name"] == folder_name:
            print("已发现目标文件夹")
            print(f'ID: {i["folder_id"][1:]}')
            break
    else:
        print("未发现目标文件夹")
elif get_type == "n":
    target_folder_id = input("输入父文件夹ID(可使用获取根目录下文件夹ID获取)：")
    filelist = requests.post(BOT_ROOT+f"/get_group_files_by_folder?access_token={BOT_TOKEN}",data=json.dumps(
        {
            "group_id": int(group_id),
            "folder_id": target_folder_id
        }
    )).json()
    folders = filelist["data"]["folders"]
    for i in folders:
        if i["folder_name"] == folder_name:
            print("已发现目标文件夹")
            print(f'ID: {i["folder_id"][1:]}')
            break
    else:
        print("未发现目标文件夹")
else:
    print("输入错误")