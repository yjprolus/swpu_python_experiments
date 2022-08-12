import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler

# 读取训练数据和测试数据
train_csv = pd.read_csv("train.csv", encoding='gb18030')
test_csv = pd.read_csv("test.csv", encoding='gb18030')

train_x = train_csv[train_csv['测项'] == 'PM2.5'].drop(['日期', '测站', '测项'], axis=1).astype(float).values[:, 8].reshape(
    -1, 1)  # 第八个小时的PM2.5作为特征变量
train_y = train_csv[train_csv['测项'] == 'PM2.5'].drop(['日期', '测站', '测项'], axis=1).astype(float).values[:, 9]

train_x_ss = StandardScaler().fit_transform(train_x)

# 建立一元线性回归模型
model = SGDRegressor()
model.fit(train_x_ss, train_y)
w = model.coef_
b = model.intercept_
print(w, b)
print("评分：", model.score(train_x_ss, train_y))

# 图形化显示
plt.figure(figsize=(10, 6))
plt.scatter(train_x_ss, train_y)
plt.plot(train_x_ss, w * train_x_ss - b, 'r')
plt.show()

print("学号_姓名")
