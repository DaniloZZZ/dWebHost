from python:3.6
workdir /home/danlkv/dWebHost

copy requirements.txt ./
run pip install --no-cache-dir -r requirements.txt
COPY . .
expose 5000
entrypoint ["python","-u", "./Node.py"]
