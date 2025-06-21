from flask import Blueprint, redirect, url_for, flash, send_file, jsonify, session, request
from flask_login import login_required
from models.prediction_model import run_model
import pandas as pd
import io

model_bp = Blueprint('model', __name__)

@model_bp.route('/run-model')
@login_required
def run_model_route():
    try:
        results = run_model()
        flash('Model executed successfully!', 'success')
        return redirect(url_for('main.home'))
    except Exception as e:
        flash(f'Model execution failed: {str(e)}', 'danger')
        return redirect(url_for('main.home'))

@model_bp.route('/export-results')
@login_required
def export_results():
    try:
        results = run_model()
        df = pd.DataFrame(results['data'])
        output = io.BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='model_results.csv',
            mimetype='text/csv'
        )
    except Exception as e:
        flash(f'Export failed: {str(e)}', 'danger')
        return redirect(url_for('main.home'))

@model_bp.route('/set-fruit', methods=['POST'])
@login_required
def set_fruit():
    selected_fruit = request.json.get('fruit')
    session['selected_fruit'] = selected_fruit
    return jsonify({
        'status': 'success', 
        'fruit': selected_fruit,
        'message': f"Now analyzing {selected_fruit}" if selected_fruit else "Selection cleared"
    })