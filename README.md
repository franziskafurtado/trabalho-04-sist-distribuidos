Para rodar o projeto é necessário instalar o Flask, o pika, o flask-cors, o chocolatey, o rabbitmq conforme:\**
instalar o python\**
pip install flask\**
pip3 install pika\**
pip install flask pika flask-cors\**
Instalar chocolatey: (Powershell como adm) \**
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))\**
choco install rabbitmq admin\**
rodar rabbitmq\**
rodar: python principal.py\**
pip show requests\**






