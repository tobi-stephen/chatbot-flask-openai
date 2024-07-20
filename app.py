from flask import Flask, jsonify, request, render_template
from utils import Chain


app = Flask(__name__)
chain = None  # To be set in the `set_context` api
subjects = ["World", "Politics", "General", "Food", "Family"]


@app.get('/health')
def health():
    return jsonify({'status': 'success', 'msg': 'all is well!'})

@app.get('/')
@app.get('/welcome')
def welcome():
    return render_template('index.html')


@app.post('/context')
def set_context():
    global chain

    # we expect `subject`, `source`, and `resource`
    data = request.get_json()
    subject = data.get('subject')
    source = data.get('source')
    resource = data.get('resource')
    if not subject:
        return jsonify({'status': 'failure', 'msg': 'provide a subject matter'}), 400
    
    chain = Chain(subject, source, resource)

    return jsonify({'status': 'success', 'msg': 'context added'})


@app.post('/assistant')
def chat_assistant():
    global chain
    
    warning = ''
    if not chain:
        warning = 'set context for better results!'
        chain = Chain(''.join(subjects))
    
    data = request.get_json()

    # we expect `question` field
    if not data.get('question'):
        return jsonify({'status': 'failure', 'msg': 'provide a question'}), 400
    
    question = data.get('question')
    response = chain.invoke(question)

    return jsonify({'status': 'success', 'msg': {'question': question, 'response': response}, 'warning': warning})


@app.errorhandler(Exception)
def error_handler(e: Exception):
    if isinstance(e, ValueError):
        return jsonify({'status': 'failure', 'msg': str(e)}), 400
    
    return jsonify({'status': 'failure', 'msg': f'server error: {str(e)}'}), 400
    

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        pass