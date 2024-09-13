from flask import Flask, request, redirect, url_for, render_template, send_file, abort
import pandas as pd
import os
import tempfile
from analyze_function import analyze_top_fields

app = Flask(__name__)

# Directory for uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variable to store the dataset
dataset = None
result_file_path = None  # Initialize the global variable for result file path

@app.route("/", methods=['GET', 'POST'])
def index():
    global dataset
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                dataset = pd.read_csv(file_path)

                # Get dynamic dropdown options from the dataset
                group_by_cols = dataset.columns.tolist()
                sort_by_cols = dataset.columns.tolist()
                agg_options = {'first': 'Display_column', 'nunique': 'Unique Count', 'sum': 'Sum'}

                return render_template('index1.html', dataset_loaded=True, group_by_cols=group_by_cols, sort_by_cols=sort_by_cols, agg_options=agg_options)
    
    return render_template('index1.html', dataset_loaded=False)

@app.route('/analyze', methods=['POST'])
def analyze():
    global dataset, result_file_path  # Declare the global variables
    if request.method == 'POST':
        if dataset is None:
            return redirect(url_for('index'))

        # Collect the form data
        group_by_col = request.form.get('group_by_col')
        sort_by_col = request.form.get('sort_by_col')

        # Collect aggregate fields and types dynamically
        agg_dict = {}
        for i in range(1, int(request.form.get('num_agg_fields', 1)) + 1):
            field = request.form.get(f'agg_field{i}')
            agg_type = request.form.get(f'agg_type{i}')
            if field and agg_type:
                agg_dict[field] = agg_type
        
        top_n = int(request.form.get('top_n'))
        display_mode = request.form.get('display_mode') or 'None'

        # Create a temporary file for results
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            result_file_path = temp_file.name

        analyze_top_fields(dataset, [group_by_col], agg_dict, sort_by_col, top_n, result_file_path, empty_fields=[], display_mode=display_mode)
        
        # Read the result file and prepare data for the results page
        result_df = pd.read_csv(result_file_path)
        columns = result_df.columns.tolist()
        rows = result_df.values.tolist()

        # Render results in a template with a download link
        return render_template('results.html', columns=columns, rows=rows)

@app.route('/download')
def download_file():
    global result_file_path
    # Serve the file from the temporary directory
    if result_file_path is None or not os.path.exists(result_file_path):
        abort(404)
    
    return send_file(result_file_path, as_attachment=True, download_name='result.csv')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
