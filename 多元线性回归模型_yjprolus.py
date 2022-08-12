import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# 读取训练数据和测试数据
train_csv = pd.read_csv("train.csv", encoding='gb18030')
test_csv = pd.read_csv("test.csv", encoding='gb18030')

train_x = train_csv[train_csv['测项'] == 'PM2.5'].drop(['日期', '测站', '测项'], axis=1).astype(float).values[:, 0:9]
train_y = train_csv[train_csv['测项'] == 'PM2.5'].drop(['日期', '测站', '测项'], axis=1).astype(float).values[:, 9]
# train_x, train_y,test_x,test_y = train_test_split(train_x, train_y)

# 建立多项式性回归模型
model = LinearRegression()
model.fit(train_x, train_y)
w = model.coef_  # 系数
b = model.intercept_  # 截距
print("系数：{}\n截距：{}".format(w, b))

# 建立多个变量与PM2.5之间的预测模型，并用均方误差和score()来检测模型好坏
predict_y = model.predict(
    train_csv[train_csv['测项'] == 'PM2.5'].drop(['日期', '测站', '测项'], axis=1).astype(float).values[:, 1:10])
real_y = train_csv[train_csv['测项'] == 'PM2.5'].drop(['日期', '测站', '测项'], axis=1).astype(float).values[:, 10]
error = mean_squared_error(real_y, predict_y)
# error = np.mean((train_x - predict_y) ** 2)
print("\n预测的均方误差：", error)
print("模型的分数：", model.score(train_x, predict_y))

# plt.figure(figsize=(10, 6))
# plt.scatter(train_x, predict_y)
# plt.show()

print("学号_姓名")
