import cv2
import numpy as np
from progressbar import ProgressBar


def read_challenges(filedir="AVA_dataset/challenges.txt"):
    f = open(filedir, "r")
    lines = f.readlines()
    for line in lines:
        print(line)


def read_tags(filedir="AVA_dataset/tags.txt"):
    f = open(filedir, "r")
    lines = f.readlines()
    for line in lines:
        print(line)


class AVAImages:
    def __init__(self):
        self.image_url = []
        self.score = []
        self.cat = []
        self.challenge = []
        self.batch_index = 0
        self.batch_num = 0

    def load_data(self, filedir="AVA_dataset/AVA.txt", train_prob=0.96, test_prob=0.0001, val_prob=0.0001):
        """
        :param filedir:

        :var image_url: int array
        :var score: float list
        :var cat: 60*2 one-hot array
        :var challenge: int list
        :var batch_index: int
        """

        f = open(filedir, "r")
        lines = f.readlines()
        for line in lines:
            seg = line.split(" ")
            seg = list(map(int, seg))
            self.image_url.append(seg[1])
            self.score.append(self.cal_score(seg[2:12]))
            if seg[12] == 0:
                p1 = np.zeros(66)
            else:
                p1 = np.eye(66)[seg[12]-1]
            if seg[13] == 0:
                p2 = np.zeros(66)
            else:
                p2 = np.eye(66)[seg[13]-1]
            self.cat.append(np.hstack((p1, p2)))
            self.challenge.append(seg[14])

        # to array
        self.image_url = np.array(self.image_url)
        self.cat = np.array(self.cat)
        self.score = np.array(self.score)

        # shuffle
        index = [i for i in range(self.image_url.shape[0])]
        np.random.shuffle(index)
        np.random.shuffle(index)
        np.random.shuffle(index)
        self.image_url = self.image_url[index]
        self.cat = self.cat[index]
        self.score = self.score[index]

        # split
        print("train set: 0->{end}".format(end=int(self.image_url.shape[0]*train_prob)))
        self.train_set_x = self.image_url[0: int(self.image_url.shape[0]*train_prob)]
        self.train_set_y_tag = self.cat[0: int(self.image_url.shape[0]*train_prob)]
        self.train_set_y_score = self.score[0: int(self.image_url.shape[0] * train_prob)]

        # url to image
        print("loading test images ... {st}->{ed}".format(st=int(self.image_url.shape[0] * train_prob),
                                                          ed=int(self.image_url.shape[0] * (train_prob + test_prob))))
        y_ori = self.cat[int(self.image_url.shape[0] * train_prob): int(self.image_url.shape[0] * (train_prob + test_prob))], \
                self.score[int(self.image_url.shape[0] * train_prob): int(self.image_url.shape[0] * (train_prob + test_prob))]
        self.test_set_x, self.test_set_y_tag, self.test_set_y_score = self.urls_to_images(
            self.image_url[int(self.image_url.shape[0] * train_prob): int(self.image_url.shape[0] * (train_prob + test_prob))],
            y_ori
        )
        print("loading validation images ... {st}->{ed}".format(st=int(self.image_url.shape[0] * (train_prob + test_prob)),
                                                                ed=int(self.image_url.shape[0] * (train_prob + test_prob + val_prob))))
        y_ori = self.cat[int(self.image_url.shape[0] * (train_prob + test_prob)):
                         int(self.image_url.shape[0] * (train_prob + test_prob + val_prob))],\
                self.score[int(self.image_url.shape[0] * (train_prob + test_prob)):
                           int(self.image_url.shape[0] * (train_prob + test_prob + val_prob))]
        self.val_set_x, self.val_set_y_tag, self.val_set_y_score = self.urls_to_images(
            self.image_url[int(self.image_url.shape[0] * (train_prob + test_prob)):
                           int(self.image_url.shape[0] * (train_prob + test_prob + val_prob))],
            y_ori
        )

    def cal_score(self, score_distribution: list):
        """以均分作为图像的分数"""
        total = score_distribution[0] * 1 \
            + score_distribution[1] * 2 \
            + score_distribution[2] * 3 \
            + score_distribution[3] * 4 \
            + score_distribution[4] * 5 \
            + score_distribution[5] * 6 \
            + score_distribution[6] * 7 \
            + score_distribution[7] * 8 \
            + score_distribution[8] * 9 \
            + score_distribution[9] * 10
        return total / sum(score_distribution)

    def urls_to_images(self, urls, y_ori, filedir="AVA_dataset/images/", flag=1):
        # print('{name}: {age}'.format(age=24, name='TaoXiao'))  # 通过关键字传递
        y_ori_1, y_ori_2 = y_ori
        # print("before url to images: {url_num}, {y_num}".format(url_num=urls.shape[0], y_num=y_ori_1.shape[0]))
        images = []
        y1 = []
        y2 = []
        i = 0

        if flag == 1:
            progress = ProgressBar(urls.shape[0])
            progress.start()

            for url in urls:
                img = cv2.imread(filedir + str(url) + ".jpg")
                if img is not None:
                    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
                    images.append(img)
                    y1.append(y_ori_1[i])
                    y2.append(y_ori_2[i])
                i += 1
                progress.show_progress(i)
            progress.end()
        else:
            for url in urls:
                img = cv2.imread(filedir + str(url) + ".jpg")
                if img is not None:
                    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)
                    images.append(img)
                    y1.append(y_ori_1[i])
                    y2.append(y_ori_2[i])
                i += 1

        # print("after url to images: {url_num}, {y_num}".format(url_num=len(images), y_num=len(y1)))
        return np.array(images)/225., np.array(y1), np.array(y2)[:, np.newaxis]

    def load_next_batch(self, batch_size: int):
        """
        :param batch_size:
        :return: x_batch, y_batch

        :var x_batch: (batch size, width, height, channels)
        """
        batch_end_flag = 0
        # print("loading batch images ...")

        if self.batch_num == 0:
            self.batch_num = self.train_set_x.shape[0] // batch_size
        if self.batch_index == self.batch_num:
            print("last batch!")
            x_urls = self.train_set_x[self.batch_index * batch_size: self.train_set_x.shape[0]]
            y1 = self.train_set_y_tag[self.batch_index * batch_size: self.train_set_x.shape[0]]
            y2 = self.train_set_y_score[self.batch_index * batch_size: self.train_set_x.shape[0]]
            self.batch_index = 0
            batch_end_flag = 1
        else:
            # print("batch {id1}->{id2}/{total}".format(id1=self.batch_index, id2=self.batch_index+1,total=self.batch_num))
            x_urls = self.train_set_x[self.batch_index*batch_size: (self.batch_index+1)*batch_size]
            y1 = self.train_set_y_tag[self.batch_index*batch_size: (self.batch_index+1)*batch_size]
            y2 = self.train_set_y_score[self.batch_index * batch_size: (self.batch_index + 1)*batch_size]
            self.batch_index += 1
        y_ori = y1, y2
        x_batch, y_batch_tag, y_batch_score = self.urls_to_images(x_urls, y_ori, flag=0)
        return x_batch, y_batch_tag, y_batch_score, batch_end_flag

    def load_val_set(self):
        return self.val_set_x, self.val_set_y_tag
