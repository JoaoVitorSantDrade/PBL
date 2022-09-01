FROM python:3.10.5

ADD Config.py .
ADD Hidrante.py .
ADD Main.py .
ADD Socket.py .

CMD ["python","./Main.py"]