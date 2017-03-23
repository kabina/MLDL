import tensorflow as tf, sys
import cv2
import time
from gtts import gTTS
import os
from GOOGLE_INCEPTION import motion_track_adv
from chatterbot import ChatBot

# Create a new chat bot named Charlie
chatbot = ChatBot('Example Bot')

def tts(text) :
    tts = gTTS(text, lang='en')
    tts.save("/tmp/pcvoice.mp3")

    # subprocess.check_output(["potplayer"])
    # this is for linux
    os.system("cmdmp3"
              " /tmp/pcvoice.mp3")

#cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()

else:
    rval = False
count = 0


while True:

    isFound, foundImg = motion_track_adv.motionTrack()

    if isFound:
        ttsstr = "hello there?"
        tts(ttsstr)
        time.sleep(1)
    else:
        continue

    #image_data = tf.gfile.FastGFile(foundImg, 'rb').read()
    image_data = tf.image.decode_png(foundImg)
    print(image_data)
    print(image_data.shape)


    # Loads label file, strips off carriage return
    label_lines = [line.rstrip() for line
                   in tf.gfile.GFile("e:/tf_files/retrained_labels.txt")]

    # Unpersists graph from file
    with tf.gfile.FastGFile("e:/tf_files/retrained_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')
    #shape = (int("1500"), int("1500"))
    #with tf.device("/gpu:0"):
    #    random_matrix = tf.random_uniform(shape=shape, minval=0, maxval=1)
    #    dot_operation = tf.matmul(random_matrix, tf.transpose(random_matrix))
    #    sum_operation = tf.reduce_sum(dot_operation)

    with tf.Session() as sess:
        # Feed the image_data as input to the graph and get first prediction
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

        predictions = sess.run(softmax_tensor, \
                               {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

        post_human_string = ""
        for node_id in top_k:
            human_string = label_lines[node_id]
            score = predictions[0][node_id]
            print('%s (score = %.5f)' % (human_string, score))

            if(score > 0.5) :

                if(human_string=="nheo") :
                    human_string = "reo"
                if(human_string=="juha") :
                    human_string = "maizy"

                if(post_human_string==human_string) :
                    break;
                post_human = human_string

                ttsstr = "hello %s"%human_string
                tts(ttsstr)


    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break
cv2.destroyWindow("preview")
