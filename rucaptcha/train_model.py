import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'   # disable a lot of tensorflow info

import tensorflow as tf
import numpy as np
from PIL import Image


H, W, C = 70, 200, 1 # height width channel( color)

CHARLIST = 'abcdfhijklmnopqrstuvwxyz'
MAP = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'f': 4, 'h': 5, 'i': 6, 'j': 7, 'k': 8, 'l': 9, 'm': 10, 'n': 11, 'o': 12, 'p': 13, 'q': 14, 'r': 15, 's': 16, 't': 17, 'u': 18, 'v': 19, 'w': 20, 'x': 21, 'y': 22, 'z': 23} 

### output vector 5 chars in CHARLIST
N_LABELS = len("abcdfhijklmnopqrstuvwxyz") 
D = 5  # char count 


from io import BytesIO

import ctypes
# from rucaptcha.c
GIFSIZE = 17646 
# build librucaptcha.so via `cc  -fPIC rucaptcha.c -shared -o librucaptcha.so`
rucaptcha = ctypes.cdll.LoadLibrary("./librucaptcha.so")


def get_data_generator( batch_size = 16):
    images, labels = [], []

    while True:
        l = ctypes.create_string_buffer(D)
        gif_p =  ctypes.create_string_buffer(GIFSIZE)

        rucaptcha.work(gif_p,l)
        name = l.value
        gif = gif_p.raw
        #  value only 0 and 15 16bit mode
        im = Image.open(BytesIO(gif)) 
        im = np.array(im) 
        images.append(im)
        labels.append([np.array(tf.keras.utils.to_categorical(MAP[chr(i)], N_LABELS)) for i in name])
        if len(images) >= batch_size:
            yield np.array(images) , np.array(labels)
            images, labels = [], []

    pass


input_layer = tf.keras.Input(shape=(H, W , C))
x = tf.keras.layers.Conv2D(16, 3, activation='relu')(input_layer) #32
x = tf.keras.layers.MaxPooling2D((2, 2))(x)
x = tf.keras.layers.Conv2D(32, 3, activation='relu')(x) #64
x = tf.keras.layers.MaxPooling2D((2, 2))(x)
x = tf.keras.layers.Conv2D(32, 3, activation='relu')(x) #64
x = tf.keras.layers.MaxPooling2D((2, 2))(x)
# 64 32 16 flat 1024 tflite 2.7M model 32M  2,785,576 params with loss 0.0160 acc 0.9949 epoch 25 step 1000


# size based on flatten (  last polling H 7 *W 23 *C  last conv2d filtersize    ) * dense
# last W = (( (200 - kernelsize1 ) /pooling_size1 ) - kernel_size2) / pooling_size2 ...

x = tf.keras.layers.Flatten()(x)
x = tf.keras.layers.Dense(256, activation='relu')(x) #1024

x = tf.keras.layers.Dense(D * N_LABELS, activation='softmax')(x)
x = tf.keras.layers.Reshape((D, N_LABELS))(x)

model = tf.keras.models.Model(inputs=input_layer, outputs=x)

model.compile(optimizer='adam', 
              loss='categorical_crossentropy',
              metrics= ['accuracy'])
model.summary()

from tensorflow.keras.callbacks import ModelCheckpoint

batch_size = 64
valid_batch_size = 64
train_gen = get_data_generator( batch_size=batch_size)
valid_gen = get_data_generator( batch_size=valid_batch_size)

callbacks = [
    ModelCheckpoint("./model_checkpoint", monitor='val_loss')
]


history = model.fit(train_gen,
                    steps_per_epoch=1000,
                    epochs=40, #25
                    # callbacks=callbacks,
                    validation_data=valid_gen,
                    validation_steps=500,
                    verbose=2)
model.save("rucaptcha_model")



# ###tflite
converter = tf.lite.TFLiteConverter.from_saved_model('rucaptcha_model')
converter.optimizations = [ tf.lite.Optimize.DEFAULT]
with open("rucaptcha.tflite","wb") as f:
    f.write(converter.convert())

### use
##1) use tensorflow
# model = tf.keras.models.load_model("rucaptcha_model")
# img = Image.open("rucaptcha.gif")
# img_array = np.array(img) 
# res = model(np.array([ img_array ]))
# print("".join([ CHARLIST[i] for i in res.numpy().argmax(axis = -1)[0]]))

##2) use tflite
# from PIL import Image
# import tensorflow.lite as tflite
# img = Image.open("rucaptcha.gif")
# interpreter = tflite.Interpreter(model_path="rucaptcha.tflite")

# interpreter.allocate_tensors()

# # Get input and output tensors.
# input_details = interpreter.get_input_details()
# output_details = interpreter.get_output_details()

# input_data = np.array(np.array(img).reshape(input_details[0]['shape'])).astype('float32')
# interpreter.set_tensor(input_details[0]['index'], input_data)

# interpreter.invoke()
# output_data = interpreter.get_tensor(output_details[0]['index'])
# print("".join([ CHARLIST[i] for i in output_data.argmax(axis = -1)[0]]))
