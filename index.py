from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# 读取CSV文件
csv_file_path = './amazon-reviews.csv'
df = pd.read_csv(csv_file_path)
us_cities_csv_file_path = 'us-cities.csv'
df_us_cities = pd.read_csv(us_cities_csv_file_path)

user_info = {
        'name': 'Yu Wang',
        'id': '76001'
    }
@app.route('/')
def index():
    # 在这里添加你的姓名、ID和照片的信息

    return render_template('index.html', user_info=user_info)


@app.route('/reviews')
def reviews():
    # 将CSV文件的内容传递给模板
    reviews_data = df[['score', 'city', 'title', 'review']].to_dict(orient='records')
    return render_template('reviews.html', reviews_data=reviews_data, user_info=user_info)


@app.route('/us-cities')
def us_cities():
    # 获取查询参数
    selected_city = request.args.get('city', '')

    # 如果有查询参数，只显示对应城市信息，否则显示所有城市信息
    if selected_city:
        cities_data = df_us_cities[df_us_cities['city'] == selected_city].to_dict(orient='records')
    else:
        cities_data = df_us_cities.to_dict(orient='records')

    return render_template('us_cities.html', cities_data=cities_data, user_info=user_info)


if __name__ == '__main__':
    app.run(debug=True)
