import tensorflow as tf
import numpy as np
model_buy = tf.keras.models.load_model('buy.h5')
me = np.array([[5,1,2,0,1,3]])
out = model_buy.predict(me)
oo = [np.argmax(out), out[0][0], out[0][1]]
print(oo)

