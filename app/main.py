from flask import Flask, request, jsonify
from ai import TextSummarizer
from scraper import load_article_content, get_article_urls_from_web, RESULT_COUNT
import pandas as pd
import json

def create_app():
    app = Flask(__name__)
    summarizer = TextSummarizer()

    @app.route('/')
    def health_check():
        return "OK"
    
    @app.route('/api/summarize', methods=['GET', 'POST'])
    def summarize():
        content = request.json
        urls = list(content["urls"])
        summaries = {}
        for url in urls:
            content = load_article_content(url)
            summary = summarizer.summarize(content)
            summaries[url] = summary
        summaries["meta_summary"] = summarizer.summarize('\n\n'.join(summaries.values()))

        return jsonify(summaries)
    
    @app.route('/api/list_articles', methods=['GET', 'POST'])
    def list_articles():
        content = request.json
        url = content["url"]
        df = pd.DataFrame(get_article_urls_from_web(url))
        df = df.sort_values('timestamp', ascending=False).head(RESULT_COUNT).reset_index(drop=True)
        lines =  df.to_json(orient='records', lines=True, force_ascii=False).splitlines()
        for i, line in enumerate(lines):
            lines[i] = json.loads((line.replace('\\', '')))
        return lines

    return app
