FROM python:2.7
ADD evaluator.py /
ADD parser.py /
ADD robot.urdf /
RUN pip install xmltodict
RUN pip install pybullet
RUN pip install elasticsearch
RUN pip install redis
CMD ["python", "./evaluator.py"]
