import tensorflow as tf
from tensorflow import keras
import os

from ClassifierData import getGestureData

def makeModel(image_shape):
    i = tf.keras.Input(shape=image_shape)
    x = keras.layers.Conv2D(32, (5, 5))(i)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.Activation('relu')(x)
    x = keras.layers.MaxPool2D(pool_size=(2,2))(x)
    x = keras.layers.Conv2D(64, (3, 3))(x)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.Activation('relu')(x)
    x = keras.layers.MaxPool2D(pool_size=(2,2))(x)
    x = keras.layers.Conv2D(32, (3, 3))(x)
    x = keras.layers.BatchNormalization()(x)
    x = keras.layers.Activation('relu')(x)
    x = keras.layers.Flatten()(x)
    out = keras.layers.Dense(3, 'softmax')(x)
    return tf.keras.Model(i, out)

if __name__=="__main__":
    print(tf.__version__)
    image_size = (32, 32)
    directory = "Data/"
    if not os.path.isdir(directory):
        getGestureData()
    if not os.path.isdir(directory):
        print('Error downloading training data.\n'
              'Please try manually downloading dataset.\n')
        exit(0)

    train_ds = keras.utils.image_dataset_from_directory(
        directory,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=image_size,
        batch_size=32)
    val_ds = keras.utils.image_dataset_from_directory(
        directory,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=image_size,
        batch_size=32)

    print(train_ds.class_names)
    print(val_ds.class_names)

    resize_and_rescale = tf.keras.Sequential([
        keras.layers.Resizing(*image_size),
    ])

    augment = keras.Sequential([
        keras.layers.RandomFlip("horizontal"),
    ])
    model = keras.Sequential([
        resize_and_rescale,
        augment,
        makeModel((*image_size, 3))
    ])

    model.compile(optimizer=tf.keras.optimizers.Adam(),
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(),
                  metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])
    model.layers[-1].summary()
    print("Model compiled")

    model.fit(train_ds, epochs=10, validation_data=val_ds)
    model.save("NewGestureModel")
