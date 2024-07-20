from flask import Flask, jsonify, request
from utils import Chain


app = Flask(__name__)
chain = None  # To be set in the `set_context` api
subjects = ["World", "Politics", "General", "Food", "Family"]


@app.get('/welcome')
def welcome():
    return jsonify({'msg': 'welcome'})


@app.post('/context')
def set_context():
    global chain

    # we expect `subject`, `source`, and `resource`
    data = request.get_json()
    subject = data.get('subject')
    source = data.get('source')
    resource = data.get('resource')
    if not subject:
        return jsonify({'msg': 'provide a subject matter'}), 400
    
    chain = Chain(subject, source, resource)

    return jsonify({'msg': 'context added'})


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
        return jsonify({'msg': 'provide a question'}), 400
    
    question = data.get('question')
    response = chain.invoke(question)

    return jsonify({'msg': 'success', 'data': {'question': question, 'response': response}, 'warning': warning})


@app.errorhandler(Exception)
def error_handler(e: Exception):
    if isinstance(e, ValueError):
        return jsonify({'msg': str(e)})
    
    return jsonify({'msg': f'server error: {str(e)}'})
    

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        pass