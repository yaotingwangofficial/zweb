# zweb

requirements.txt
```
fastapi>=0.111
uvicorn[standard]>=0.30
pydantic>=2.7
python-multipart>=0.0.9
orjson>=3.10
cachetools>=5.3
```

```
cd backend
sh run_demo.sh
```

### run_demo.sh
`uvicorn app.main:app --host 0.0.0.0 --port 8012 --reload` 可根据需求/占用改变port.


### app/config.py
- 设定全局变量, 本地存储的数据文件结构应该按照代码中描述的那样进行配置, 而不是更改代码. 
- 但是可以更改`prefix_dir`, `data_root`等服务器内path.

