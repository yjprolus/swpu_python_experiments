import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# 读取训练数据和测试数据
train_csv = pd.read_csv("train.csv", encoding='gb18030')
test_csv = pd.read_csv("test.csv", encoding='gb18030')

train_x = train_csv[train_csv['测项'] == 'PM2.5'].drop(['日期', '测站', '测项'], axis=1).astype(float).values[:, 5].reshape(
    -1, 1)  # 第八个小时的PM2.5作为特征变量
train_y = train_csv[train_csv['测项'] == 'PM2.5'].drop(['日期', '测站', '测项'], axis=1).astype(float).values[:, 9]

poly = PolynomialFeatures(degree=2)
poly_x = poly.fit_transform(train_x)

# 建立一元多项式回归模型
model1 = LinearRegression()
model1.fit(poly_x, train_y)
poly_y_predict = model1.predict(poly_x)

model2 = LinearRegression()
model2.fit(train_x, train_y)
y_predict = model2.predict(train_x)

# 图形化显示
plt.figure(figsize=(10, 6))
plt.scatter(train_x, train_y)
plt.scatter(train_x, y_predict)
plt.scatter(train_x, poly_y_predict)
plt.show()

print(model1.coef_, model1.intercept_)
print("学号_姓名")
