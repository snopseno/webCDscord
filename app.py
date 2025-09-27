from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/fetch-avatar', methods=['POST'])
def fetch_avatar():
    data = request.json
    profile_url = data.get('profile_url')
    if not profile_url:
        return jsonify({'error': 'No profile URL provided'}), 400
    
    # Шаг 1: Автоматическое получение куки (запрос на главную страницу)
    session = requests.Session()
    main_url = 'https://anixart-app.com/'
    response = session.get(main_url)
    cookies = '; '.join([f'{k}={v}' for k, v in session.cookies.items()])
    
    # Шаг 2: Извлечение ID профиля
    match = re.search(r'/profile/(\d+)', profile_url)
    if not match:
        return jsonify({'error': 'Invalid profile URL'}), 400
    user_id = match.group(1)
    
    # Шаг 3: Запрос страницы профиля с куки
    profile_response = session.get(profile_url)
    if profile_response.status_code != 200:
        return jsonify({'error': 'Failed to fetch profile'}), 500
    
    # Шаг 4: Парсинг HTML для аватара (ищем <img> с классом avatar или src с /avatars/)
    soup = BeautifulSoup(profile_response.text, 'html.parser')
    avatar_img = soup.find('img', class_=re.compile(r'avatar|profile-icon|user-avatar', re.I))
    if not avatar_img:
        # Альтернатива: поиск по src
        avatar_img = soup.find('img', src=re.compile(r'/avatars/\d+\.(png|jpg|jpeg|webp)'))
    
    avatar_url = avatar_img['src'] if avatar_img and 'src' in avatar_img.attrs else None
    if avatar_url and not avatar_url.startswith('http'):
        avatar_url = 'https://anixart-app.com' + avatar_url
    
    if avatar_url:
        return jsonify({'avatar_url': avatar_url})
    else:
        return jsonify({'error': 'Avatar not found in profile'}), 404

if __name__ == '__main__':
    app.run(debug=True)
