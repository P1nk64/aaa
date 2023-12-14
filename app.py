from collections import Counter
import re
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd

app = Flask(__name__)

# 读取CSV文件
df_reviews_path = 'amazon-reviews.csv'
df_reviews = pd.read_csv(df_reviews_path)
us_cities_csv_file_path = 'us-cities.csv'
df_us_cities = pd.read_csv(us_cities_csv_file_path)

user_info = {
    'name': 'Yu Wang',
    'id': '6001'
}


# @app.route('/')
# def index():
#     # 在这里添加你的姓名、ID和照片的信息
#
#     return render_template('index.html', user_info=user_info)
#
#
# @app.route('/reviews')
# def reviews():
#     # 将CSV文件的内容传递给模板
#     reviews_data = df_reviews[['score', 'city', 'title', 'review']].to_dict(orient='records')
#     return render_template('reviews.html', reviews_data=reviews_data, user_info=user_info)
#
#
# @app.route('/us-cities', methods=['GET', 'POST'])
# def us_cities():
#     global df_us_cities  # 使用 global 关键字声明全局变量
#
#     if request.method == 'POST':
#         # 处理表单提交
#         city = request.form['city']
#         lat = float(request.form['lat'])
#         lng = float(request.form['lng'])
#         country = request.form['country']
#         state = request.form['state']
#         population = int(request.form['population'])
#
#         # 查找城市是否存在
#         existing_city_index = df_us_cities[df_us_cities['city'] == city].index
#
#         if not existing_city_index.empty:
#             # 更新现有城市记录
#             existing_city_index = existing_city_index[0]
#             df_us_cities.loc[existing_city_index] = {'city': city, 'lat': lat, 'lng': lng, 'country': country,
#                                                      'state': state, 'population': population}
#         else:
#             # 插入新记录
#             new_city = pd.DataFrame({'city': [city], 'lat': [lat], 'lng': [lng], 'country': [country], 'state': [state],
#                                      'population': [population]})
#             df_us_cities = pd.concat([df_us_cities, new_city], ignore_index=True)
#
#         # 保存更新后的DataFrame到CSV
#         df_us_cities.to_csv(us_cities_csv_file_path, index=False)
#
#     # 获取查询参数
#     selected_city = request.args.get('city', '')
#
#     # 如果有查询参数，只显示对应城市信息，否则显示所有城市信息
#     if selected_city:
#         cities_data = df_us_cities[df_us_cities['city'] == selected_city].to_dict(orient='records')
#     else:
#         cities_data = df_us_cities.to_dict(orient='records')
#
#     return render_template('us_cities.html', cities_data=cities_data, user_info=user_info)
#
#
# @app.route('/delete_cities', methods=['POST'])
# def delete_cities():
#     global df_us_cities  # 使用 global 关键字声明全局变量
#
#     # 获取选中的城市
#     selected_cities = request.form.getlist('selected_cities')
#
#     # 删除选中的城市
#     df_us_cities = df_us_cities[~df_us_cities['city'].isin(selected_cities)]
#
#     # 保存更新后的DataFrame到CSV
#     df_us_cities.to_csv(us_cities_csv_file_path, index=False)
#
#     return redirect(url_for('us_cities'))
#
#
@app.route('/popular_words_10', methods=['GET'])
def popular_words_10():
    # 获取查询参数
    city_name = request.args.get('city', '')
    limit = request.args.get('limit', '')

    # 根据提供的城市名过滤数据
    if city_name:
        filtered_df = pd.merge(df_reviews[df_reviews['city'] == city_name], df_us_cities, on='city')
    else:
        filtered_df = pd.merge(df_reviews, df_us_cities, on='city')

    # 组合标题和评论
    all_text = ' '.join(filtered_df['title'].astype(str) + ' ' + filtered_df['review'].astype(str))

    # 分词并统计单词数
    words = re.findall(r'\b\w+\b', all_text.lower())
    word_counts = Counter(words)

    # 获取最受欢迎的N个单词
    if limit:
        limit = int(limit)
        popular_words = [{'term': term, 'popularity': count} for term, count in word_counts.most_common(limit)]
    else:
        popular_words = [{'term': term, 'popularity': count} for term, count in word_counts.items()]

    # 根据受欢迎程度按降序对列表进行排序
    popular_words = sorted(popular_words, key=lambda x: x['popularity'], reverse=True)

    return jsonify(popular_words)


@app.route('/popular_words_11', methods=['GET'])
def popular_words_11():
    # 获取查询参数
    city_name = request.args.get('city', '')
    limit = request.args.get('limit', '')

    # 根据提供的城市名过滤数据
    if city_name:
        filtered_df = pd.merge(df_reviews[df_reviews['city'] == city_name], df_us_cities, on='city')
    else:
        filtered_df = pd.merge(df_reviews, df_us_cities, on='city')

    # 组合标题和评论
    all_text = ' '.join(filtered_df['title'].astype(str) + ' ' + filtered_df['review'].astype(str))

    # 分词并统计单词数
    words = re.findall(r'\b\w+\b', all_text.lower())
    word_city_counts = Counter([(word, city) for word, city in zip(words, filtered_df['city'])])

    # 根据人口计算流行度
    word_popularity = {}
    for (word, city), count in word_city_counts.items():
        if word not in word_popularity:
            word_popularity[word] = 0
        # 将 int64 转换为 int
        word_popularity[word] += int(df_us_cities[df_us_cities['city'] == city]['population'].iloc[0]) * count

    # 获取最受欢迎的N个单词
    if limit:
        limit = int(limit)
        popular_words = [{'term': term, 'popularity': count} for term, count in sorted(word_popularity.items(), key=lambda x: x[1], reverse=True)[:limit]]
    else:
        popular_words = [{'term': term, 'popularity': count} for term, count in word_popularity.items()]

    # 根据流行度按降序对列表进行排序
    popular_words = sorted(popular_words, key=lambda x: x['popularity'], reverse=True)

    return jsonify(popular_words)


@app.route('/substitute_words', methods=['POST'])
def substitute_words():

    # 从请求中获取JSON数据
    data = request.get_json()

    # 从JSON数据中提取word和substitute参数
    word_to_replace = data.get('word', '')
    substitute_word = data.get('substitute', '')

    # 检查是否提供了word和substitute
    if not word_to_replace or not substitute_word:
        return jsonify({"error": "需要提供'word'和'substitute'参数。"}), 400

    # 在评论中执行单词替换
    df_reviews['review'] = df_reviews['review'].str.replace(word_to_replace, substitute_word, case=False)

    # 计算受影响的评论数量
    affected_reviews = df_reviews[df_reviews['review'].str.contains(substitute_word, case=False)].shape[0]

    # 将修改后的DataFrame保存回CSV文件（可选）
    df_reviews.to_csv(df_reviews_path, index=False)

    # 以JSON格式返回响应
    return jsonify({"affected_reviews": affected_reviews})


@app.route('/words', methods=['GET'])
def words_page():
    return render_template('words.html', user_info=user_info)


if __name__ == '__main__':
    app.run(debug=True)
