FROM python:3.11-slim

# 指定 Image 中的工作目錄
WORKDIR /code

# 將 Dockerfile 所在目錄下的所有檔案複製到 Image 的工作目錄 /code 底下
ADD . /code

# 在 Image 中執行的指令：安裝 requirements.txt 中所指定的 dependencies
RUN pip install -r requirements.txt

# 創建必要的目錄
RUN mkdir -p src/history src/resources

# Google Gemini API Key (Required)
ENV API_KEY=${API_KEY}

# MQTT Broker Configuration
ENV MQTT_BROKER_HOST=${MQTT_BROKER_HOST:-localhost}
ENV MQTT_BROKER_PORT=${MQTT_BROKER_PORT:-1883}
ENV MQTT_USERNAME=${MQTT_USERNAME}
ENV MQTT_PASSWORD=${MQTT_PASSWORD}

# MQTT Topic for IoT Devices (use # wildcard for all subtopics)
ENV topic_for_iot=${topic_for_iot:-brandon/iot/zwave/philio/event/#}

# Volume for persistent chat history
VOLUME ["/code/src/history"]

# Expose Flask port
EXPOSE 5000

# Container 啟動指令：Container 啟動後通過 python 運行 server.py
WORKDIR /code/src
CMD ["python", "server.py"]