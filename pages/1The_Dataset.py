#Input the relevant libraries
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import datasets, layers, models
from tensorflow.keras.datasets import cifar10
from tensorflow.keras.utils import to_categorical


import time

# Define the Streamlit app
def app():

    if "model" not in st.session_state:
        st.session_state.model = []
    
    if "train_images" not in st.session_state:
        st.session_state.training_images = []

    text = """The CIFAR-10 dataset is a collection of 60,000 small, 
    colorful images (32x32 pixels) that belong to 10 distinct categories, 
    like airplanes, cars, and animals. It's a popular choice for 
    training machine learning algorithms, especially those focused on image 
    recognition, because it's easy to access and allows researchers to 
    experiment with different approaches quickly due to the relatively 
    low resolution of the images."""
    st.write(text)

    progress_bar = st.progress(0, text="Loading 70,000 images, please wait...")

    # Load the CIFAR-10 dataset
    (train_images, train_labels), (test_images, test_labels) = datasets.cifar10.load_data()

    #save objects to session state
    st.session_state.training_images = train_images

    train_labels = to_categorical(train_labels)
    test_labels = to_categorical(test_labels)

    with st.expander("Click to display the list of classes in the CIFAR-10 Dataset."):
        # Define CIFAR-10 class names
        class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

        # Enumerate the classes
        for i, class_name in enumerate(class_names):
            st.write(f"Class {i+1}: {class_name}")

    # update the progress bar
    for i in range(100):
        # Update progress bar value
        progress_bar.progress(i + 1)
        time.sleep(0.01)
    # Progress bar reaches 100% after the loop completes
    st.success("Image dataset loading completed!") 

    # Create the figure and a grid of subplots
    fig, axes = plt.subplots(nrows=5, ncols=5, figsize=(6, 8))

    # display images starting with index 500
    start_index = 500
    # Iterate through the subplots and plot the images
    for i, ax in enumerate(axes.flat):
        # Turn off ticks and grid
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)

        # Display the image
        ax.imshow(train_images[start_index + i], cmap=plt.cm.binary)
        # Add the image label
        ax.set_xlabel(train_labels[i][0])

    # Show the plot
    plt.tight_layout()  # Adjust spacing between subplots
    st.pyplot(fig)

    # Normalize pixel values to be between 0 and 1
    train_images, test_images = train_images / 255.0, test_images / 255.0

   # Define CNN parameters    
    st.sidebar.subheader('Set the CNN Parameters')
    options = ["relu", "leaky_relu", "sigmoid"]
    c_activation = st.sidebar.selectbox('Input activation function:', options)

    options = ["softmax", "relu"]
    o_activation = st.sidebar.selectbox('Output activation function:', options)

    hidden_layers = st.sidebar.slider(      
        label="How many hidden layers? :",
        min_value=16,
        max_value=128,
        value=64,  # Initial value
        step=16
    )

    epochs = st.sidebar.slider(   
        label="Set the epochs:",
        min_value=3,
        max_value=30,
        value=3
    )

    # Define the CNN architecture
    model = keras.Sequential(
        [
            layers.Conv2D(32, (3, 3), activation=c_activation, input_shape=(32, 32, 3)),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Conv2D(hidden_layers, (3, 3), activation=c_activation),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Conv2D(hidden_layers, (3, 3), activation=c_activation),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(10, activation=o_activation),
        ]
    )

    # Compile the model
    model.compile(
        loss="categorical_crossentropy",
        optimizer="adam",
        metrics=["accuracy"],
    )

    if st.button('Start Training'):
        progress_bar = st.progress(0, text="Training the model please wait...")
        # Train the model
        batch_size = 64
        
        history = model.fit(train_images, train_labels, batch_size=batch_size, epochs=epochs, 
                  validation_data=(test_images, test_labels), callbacks=[CustomCallback()])
        
        # Evaluate the model on the test data
        loss, accuracy = model.evaluate(test_images, test_labels)
        st.write("Test accuracy:", accuracy)

        # Extract loss and accuracy values from history
        train_loss = history.history['loss']
        val_loss = history.history['val_loss']
        train_acc = history.history['accuracy']
        val_acc = history.history['val_accuracy']

        # Create the figure and axes
        fig, ax1 = plt.subplots()

        # Plot loss on primary axis (ax1)
        ax1.plot(train_loss, label='Training Loss')
        ax1.plot(val_loss, label='Validation Loss')

        # Create a twin axis for accuracy (ax2)
        ax2 = ax1.twinx()

        # Plot accuracy on the twin axis (ax2)
        ax2.plot(train_acc, 'g--', label='Training Accuracy')
        ax2.plot(val_acc, 'r--', label='Validation Accuracy')

        # Set labels and title
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax2.set_ylabel('Accuracy')
        fig.suptitle('Training and Validation Loss & Accuracy')

        # Add legends
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right') 
        st.pyplot(fig)   

        # update the progress bar
        for i in range(100):
            # Update progress bar value
            progress_bar.progress(i + 1)
            # Simulate some time-consuming task (e.g., sleep)
            time.sleep(0.01)
        # Progress bar reaches 100% after the loop completes
        st.success("Model training completed!") 
        st.write("Use the sidebar to open the Performance page.")

        # Save the trained model to memory
        st.session_state.model = model

# Define a custom callback function to update the Streamlit interface
class CustomCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        # Get the current loss and accuracy metrics
        loss = logs['loss']
        accuracy = logs['accuracy']
        
        # Update the Streamlit interface with the current epoch's output
        st.write(f"Epoch {epoch}: loss = {loss:.4f}, accuracy = {accuracy:.4f}")

#run the app
if __name__ == "__main__":
    app()
