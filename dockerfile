FROM python:3.10.5

ADD Config.py .
ADD Hidrante.py .
ADD Socket.py .
ADD Hidrometro.py .
ADD Nuvem.py .
ADD template.html .

CMD ["python","./Nuvem.py"]