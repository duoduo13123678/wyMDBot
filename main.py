import requests
import json
import fastapi
import uvicorn
import re

BOT_ROOT = "http://127.0.0.1:3000"          #OneBot HTTP地址
BOT_TOKEN = "YOUR_TOKEN_HERE"               #OneBot的Token
MUSIC_API_ROOT = "http://127.0.0.1:5000"    #网易云音乐API项目的地址
GROUPS = {0:"文件夹ID"}                     #响应群号:文件夹ID

try:
    health_result = requests.get(MUSIC_API_ROOT+"/health")
    health_result.raise_for_status()
    if not health_result.json()["success"]:
        raise requests.HTTPError
except requests.HTTPError:
    print("无法连接到网易云音乐API! (服务器状态码不是200 OK)")
    print("网易云音乐下载项目地址：https://github.com/Suxiaoqinx/Netease_url")
    print("请检查运行状态")
except requests.exceptions.ConnectionError:
    print("无法连接到网易云音乐API! ")
    print("网易云音乐下载项目地址：https://github.com/Suxiaoqinx/Netease_url")
    print("请检查运行状态")

"""
!!!No planned!!!
def search_musics(keyword:str):
    try:
        search = requests.post(MUSIC_API_ROOT+"/search",data={"keyword":keyword,"limit":15})
        search.raise_for_status()
        result = search.json()
        return result["data"]
    except requests.HTTPError:
        return {"success":False,"message":"服务器状态码不是200 OK","target":search}
"""

def song_info(id,level:str="exhigh"):
    try:
        info = requests.post(MUSIC_API_ROOT+"/song",data={"url":id,"level":level,"type":"json"})
        info.raise_for_status()
        result = info.json()
        
        # 移除或替换非法字符
        filename = f'{result["data"]["ar_name"]} - {result["data"]["name"]}.mp3'
        illegal_chars = r'[<>:"\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        filename = re.sub(r'/',',',filename)
        # 移除前后空格和点
        filename = filename.strip(' .')
        # 限制长度
        if len(filename) > 200:
            filename = filename[:200]
            
        return {"filename":f'{filename}',"data":result["data"]}
    except requests.HTTPError:
        raise fastapi.HTTPException(status_code=500, detail={"success":False,"message":"服务器状态码不是200 OK","target":info})

def upload_file(file:str,group_id:int,filename:str,folder:str):
    try:
        result = requests.post(BOT_ROOT+f'/upload_group_file?access_token={BOT_TOKEN}',data=json.dumps(
            {
                "group_id": group_id,
                "file": file,
                "name": filename,
                "folder_id": folder
            }
        ))
        result.raise_for_status()
        return result
    except requests.HTTPError:
        raise fastapi.HTTPException(status_code=500, detail={"success":False,"message":"服务器状态码不是200 OK","target":result})

app = fastapi.FastAPI()
@app.post('/msg')
async def Message(request: fastapi.Request):
    data = await request.json()
    group = data["group_id"]
    if group in GROUPS:
        sender = data["user_id"]
        try:
            role = data["sender"]["role"]
            message_id = data["message_id"]
            raw_message = data["raw_message"]
            splited_message = raw_message.split(" ")
        except KeyError:
            return
        if splited_message[0] != "云音乐":
            return
        if splited_message[1] == "下载":
            song = song_info(splited_message[2])
            filename = song["filename"]
            url = song["data"]["url"]
            ar_name = song["data"]["ar_name"]
            name = song["data"]["name"]
            print(f"调用用户：{sender}")
            message = f"⚠️准备下载：\n名称：{name}\n歌手：{ar_name}"
            print(message)
            try:
                send_message_result = requests.post(BOT_ROOT+f'/send_group_msg?access_token={BOT_TOKEN}',data=json.dumps(
                    {
                        "group_id": group,
                        "message": [
                            {
                                "type": "reply",
                                "data": {
                                    "id": message_id
                                }
                            },
                            {
                                "type":"text",
                                "data": {
                                    "text": message
                                }
                            }
                        ]
                    }
                ))
                send_message_result.raise_for_status()
            except requests.HTTPError:
                raise fastapi.HTTPException(status_code=400, detail={"success":False,"message":"服务器状态码不是200 OK","target":send_message_result})
            else:
                #music_data = requests.post(MUSIC_API_ROOT+f"/download",data={
                #    "id": splited_message[2],
                #    "quality": "exhigh"
                #}).content
                #mime_type = 'audio/mpeg'
                #b64_data = base64.b64encode(convert_id3_tags_in_memory(music_data)).decode('ascii')
                #data_url = f'data:{mime_type};base64,{b64_data}'
                upload_file(f"{MUSIC_API_ROOT}/download?id={splited_message[2]}&quality=exhigh",group,filename,GROUPS[int(group)])
                #upload_file(data_url,group,filename,GROUPS[int(group)])
                
if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=7000)