from flask import Flask, render_template, request, jsonify, Response
from deep_translator import GoogleTranslator
from bs4 import BeautifulSoup
import json
import html

app = Flask(__name__)

LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'nl': 'Dutch',
    'pl': 'Polish',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh-cn': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'tr': 'Turkish'
}

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGES)

@app.route('/translate', methods=['POST'])
def translate_html():
    data = request.json
    html_content = data['html']
    target_lang = data['target_lang']
    
    if not html_content.strip():
        return jsonify({'translated': '', 'progress': 100})

    def generate():
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            translator = GoogleTranslator(source='en', target=target_lang)
            
            # Find all text nodes that need translation
            text_nodes = [
                element for element in soup.find_all(string=True)
                if element.strip() and element.parent.name not in ['script', 'style']
            ]
            
            total_nodes = len(text_nodes)
            if total_nodes == 0:
                yield json.dumps({'translated': str(soup), 'progress': 100}) + '\n'
                return
                
            # Translate each text node and track progress
            for index, element in enumerate(text_nodes, 1):
                try:
                    # Translate text content
                    translated = translator.translate(element.strip())
                    if translated:  # Only replace if translation is successful
                        element.replace_with(translated)
                    
                    # Calculate progress percentage
                    progress = int((index / total_nodes) * 100)
                    
                    # Return progress update
                    response_data = {
                        'progress': progress,
                        'translated': str(soup)
                    }
                    yield json.dumps(response_data) + '\n'
                    
                except Exception as e:
                    print(f"Translation error for text '{element}': {str(e)}")
                    continue
                
        except Exception as e:
            yield json.dumps({'error': f"Translation error: {str(e)}"}) + '\n'

    return Response(generate(), mimetype='application/x-json-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
