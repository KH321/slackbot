from dotenv import load_dotenv
load_dotenv()
import os

# botアカウントのトークンを指定
API_TOKEN = os.environ['API_TOKEN']

# このbot宛のメッセージで、どの応答にも当てはまらない場合の応答文字列
DEFAULT_REPLY = "thanks"

# プラグインスクリプトを置いてあるサブディレクトリ名のリスト
PLUGINS = ['plugins']
