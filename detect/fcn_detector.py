#coding:utf-8
import numpy as np
import tensorflow as tf

# FcnDetector 是给P net 用的
class FcnDetector(object):
    #net_factory: which net
    #model_path: where the params'file is
    def __init__(self, net_factory, model_path):
        #create a graph
        graph = tf.Graph()
        with graph.as_default():
            #define tensor and op in graph(-1,1)
            self.image_op = tf.placeholder(tf.float32, name='input_image')
            self.width_op = tf.placeholder(tf.int32, name='image_width')
            self.height_op = tf.placeholder(tf.int32, name='image_height')
            image_reshape = tf.reshape(self.image_op, [1, self.height_op, self.width_op, 3])
            #self.cls_prob batch*2
            #self.bbox_pred batch*4
            #construct model here
            #self.cls_prob, self.bbox_pred = net_factory(image_reshape, training=False)
            #contains landmark
            # net_factory： 传入的网络结构
            self.cls_prob, self.bbox_pred, _ = net_factory(image_reshape, training=False)
            
            #allow 
            self.sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True, gpu_options=tf.GPUOptions(allow_growth=True)))
            saver = tf.train.Saver()
            #check whether the dictionary is valid
            #load 训练好的model, 读取训练好的模型参数
            model_dict = '/'.join(model_path.split('/')[:-1])
            ckpt = tf.train.get_checkpoint_state(model_dict)
            print model_path
            readstate = ckpt and ckpt.model_checkpoint_path
            assert  readstate, "the params dictionary is not valid"
            print "restore models' param"
            # 把model 里的参数 set  到session里面
            saver.restore(self.sess, model_path)
    def predict(self, databatch):
        height, width, _ = databatch.shape
        # print(height, width)
        # 直接把读取的batch 里原始图像金字塔图片 扔给 model
        # 下面两个返回值 都是二维数组
        cls_prob, bbox_pred = self.sess.run([self.cls_prob, self.bbox_pred],
                                                           feed_dict={self.image_op: databatch, self.width_op: width,
                                                                      self.height_op: height})
        # 分类的结果， 和 bounding box
        # 对于 Pnet, Rnet, landmark 只是辅助达到multi task CNN.而不输出。。只有最后的ONet输出landmark
        return cls_prob, bbox_pred
