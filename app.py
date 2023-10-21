from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import boto3
import os
import torch
from diffusers import EulerAncestralDiscreteScheduler, StableDiffusionXLPipeline
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# azureprojectの選択
# If RUNNING_IN_PRODUCTION is defined as an environment variable, then we're running on Azure
if not 'RUNNING_IN_PRODUCTION' in os.environ:
   # Local development, where we'll use environment variables.
   print("Loading config.development and environment variables from .env file.")
   app.config.from_object('azureproject.development')
else:
   # Production, we don't load environment variables from .env file but add them as environment variables in Azure.
   print("Loading config.production.")
   app.config.from_object('azureproject.production')

with app.app_context():
    app.config.update(
        SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

# 環境変数からAPIトークンとモデルIDを読み込む
auth_token = os.environ.get("huggingface-auth-token")
model_id = os.environ.get("huggingface-model-id")

# AWSの認証情報を環境変数から読み込む
aws_access_key_id = os.environ.get("aws_access_key_id")
aws_secret_access_key = os.environ.get("aws_secret_access_key")

# AWSサービスのクライアントの初期化
comprehend = boto3.client('comprehend', region_name='ap-northeast-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
translate = boto3.client('translate', region_name='ap-northeast-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# スケジューラのロード（認証トークンを使用）
scheduler = EulerAncestralDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler", use_auth_token=auth_token)

# パイプラインのロード（認証トークンを使用）
pipe = StableDiffusionXLPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16, use_auth_token=auth_token)

# CUDAにモデルを移動
pipe = pipe.to("cuda")

# Flaskアプリケーションの初期化
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def generate_image():
    image_urls = {}
    if request.method == "POST":
        prompt = request.form["prompt"]
        features = request.form["features"]
        genre = request.form["genre"]

        # 英訳
        translation_response = translate.translate_text(Text=prompt, SourceLanguageCode="ja", TargetLanguageCode="en")
        translated_text = translation_response['TranslatedText']

        # 感情分析
        sentiment_response = comprehend.detect_sentiment(Text=translated_text, LanguageCode='en')
        sentiment = sentiment_response['Sentiment']

        # キーフレーズの抽出
        keyphrases_response = comprehend.detect_key_phrases(Text=translated_text, LanguageCode='en')
        keyphrases = ', '.join([phrase['Text'] for phrase in keyphrases_response['KeyPhrases']])

        # スタイルのリスト
        styles = {
            'pokemon': 'Pokemon style',
            'pixelart': 'Pixel art style',
            'gundam': 'Robot style'
        }

# 感情に基づいて画像を生成
        for sentiment in ['POSITIVE', 'NEGATIVE']:
            if sentiment == sentiment_response['Sentiment']:
                base_prompt = f"{keyphrases}, {features}, {sentiment.lower()}"
                if genre != "normal":
                    base_prompt += f", {styles[genre]}"
                images = pipe(base_prompt, num_inference_steps=20).images
                image_path = f"static/images/{base_prompt}.png"
                images[0].save(image_path)
                image_urls[f"{sentiment.lower()}_keyphrase_image"] = image_path

    return render_template("index.html", all_keyphrase_image=image_urls.get("POSITIVE_keyphrase_image"),
                           positive_keyphrase_image=image_urls.get("POSITIVE_keyphrase_image"),
                           negative_keyphrase_image=image_urls.get("NEGATIVE_keyphrase_image"))

if __name__ == "__main__":
    app.run(debug=True)
