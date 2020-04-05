FROM tensorflow/tensorflow:latest-gpu-py3

RUN apt-get update
RUN apt-get install -y python3-pip git libsm6 libxext6 libxrender-dev ffmpeg x264 libx264-dev

RUN git clone https://github.com/fizyr/keras-retinanet.git
WORKDIR keras-retinanet
RUN python -m pip install coverage
RUN pip3 install Pillow h5py --user
RUN pip3 install . --user
RUN python3 setup.py build_ext --inplace

COPY ./ ./app
WORKDIR ./app

RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["python3", "./app.py"]