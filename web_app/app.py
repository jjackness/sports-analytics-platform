# web_app/app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys
import json
from datetime import datetime
from data_processing.data_export import NumpyEncoder

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our simulation components
from simulation.engine import SimulationEngine
from data_processing.data_import import DataImporter
from data_processing.data_analysis import PlayByPlayAnalyzer
from data_processing.data_export import DataExporter
# Import routes
from web_app.routes import simulation

app = Flask(__name__)
app.secret_key = 'football_simulation_secret_key'  # For flash messages

# Initialize components
sim_engine = SimulationEngine(output_dir="results")
data_importer = DataImporter(data_dir="data")
data_analyzer = PlayByPlayAnalyzer()
data_exporter = DataExporter(output_dir="results")

# Register routes
simulation.init_app(app)


@app.route('/')
def index():
    """Home page with links to main features."""
    # Get list of available teams
    teams = list(sim_engine.teams.keys()) if sim_engine.teams else []
    
    # Check if we have any teams, if not create defaults
    if not teams:
        sim_engine.create_default_teams(num_teams=4)
        teams = list(sim_engine.teams.keys())
    
    return render_template('index.html', teams=teams, sim_engine=sim_engine)

@app.route('/simulation/setup', methods=['GET', 'POST'])
def simulation_setup():
    """Page to set up a new simulation."""
    teams = list(sim_engine.teams.keys()) if sim_engine.teams else []
    
    if request.method == 'POST':
        # Get simulation parameters from form
        home_team = request.form.get('home_team')
        away_team = request.form.get('away_team')
        num_simulations = int(request.form.get('num_simulations', 1))
        
        # Check if teams exist
        if home_team not in teams or away_team not in teams:
            flash('Selected teams not found', 'error')
            return redirect(url_for('simulation_setup'))
        
        # Run simulations
        try:
            # Use microseconds in timestamp for better uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            
            if num_simulations == 1:
                # Single game
                result = sim_engine.simulate_game(home_team, away_team, verbose=True)
                
                # Add simulation type and number of simulations
                result['simulation_type'] = 'single'
                result['num_simulations'] = 1
                
                # Save results to file for later viewing
                output_file = os.path.join("results", f"single_game_{timestamp}.json")
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=4)
                
                print(f"Saved single game results to: {output_file}")
                    
            else:
                # Multiple games
                result = sim_engine.run_multiple_simulations(home_team, away_team, num_sims=num_simulations)
                
                # Add simulation type and number of simulations
                result['simulation_type'] = 'multiple'
                result['num_simulations'] = num_simulations
                
                # Get team names for display
                home_team_obj = sim_engine.teams[home_team]
                away_team_obj = sim_engine.teams[away_team]
                result['home_team_name'] = getattr(home_team_obj, 'name', f"Team {home_team}")
                result['away_team_name'] = getattr(away_team_obj, 'name', f"Team {away_team}")
                
                # Save results to file for later viewing
                output_file = os.path.join("results", f"multiple_games_{timestamp}.json")
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=4, cls=NumpyEncoder)
                
                print(f"Saved multiple game results to: {output_file}")
            
            # Wait briefly to ensure file timestamp is registered
            import time
            time.sleep(0.1)
            
            return redirect(url_for('simulation_results', simulation_id='latest'))
            
        except Exception as e:
            flash(f'Error running simulation: {str(e)}', 'error')
            return redirect(url_for('simulation_setup'))
    
    return render_template('simulation/setup.html', teams=teams)

@app.route('/simulation/results/<simulation_id>')
def simulation_results(simulation_id):
    """Page to view simulation results."""
    results_dir = "results"
    
    if simulation_id == 'latest':
        # Find the latest result file - check for both single and batch simulations
        result_files = [f for f in os.listdir(results_dir) 
                         if f.endswith('.json') and (
                             f.startswith('single_game_') or 
                             f.startswith('simulation_batch_') or
                             f.startswith('multiple_games_'))]
        
        if not result_files:
            flash('No simulation results found', 'error')
            return redirect(url_for('index'))
        
        # Get full paths for each file
        result_files_with_path = [os.path.join(results_dir, f) for f in result_files]
        
        # Sort by modification time (newest first)
        latest_file_path = max(result_files_with_path, key=os.path.getmtime)
        latest_file = os.path.basename(latest_file_path)
        
        print(f"Loading latest simulation results from: {latest_file}")
        
        # Load the results
        with open(latest_file_path, 'r') as f:
            results = json.load(f)
        
        # Check if simulation_type exists, if not, try to infer it
        if 'simulation_type' not in results:
            if 'home_win_pct' in results and 'away_win_pct' in results:
                results['simulation_type'] = 'multiple'
                if 'num_simulations' not in results:
                    results['num_simulations'] = 1  # Default if not specified
            elif 'home_score' in results and 'away_score' in results:
                results['simulation_type'] = 'single'
            else:
                results['simulation_type'] = 'unknown'
        
        return render_template('simulation/results.html', results=results)
    else:
        # In future, we'd support loading specific simulation IDs
        flash('Specific simulation ID loading not implemented yet', 'error')
        return redirect(url_for('index'))

@app.route('/analysis/data')
def analysis_data():
    """Page to explore available data."""
    data_dir = "data"
    data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    return render_template('analysis/data.html', data_files=data_files)

@app.route('/analysis/run', methods=['POST'])
def run_analysis():
    """Run analysis on selected data file."""
    data_file = request.form.get('data_file')
    
    if not data_file:
        flash('No data file selected', 'error')
        return redirect(url_for('analysis_data'))
    
    # Load the data
    data_path = os.path.join("data", data_file)
    pbp_data = data_importer.import_csv(data_path)
    
    if pbp_data.empty:
        flash('Error loading data file', 'error')
        return redirect(url_for('analysis_data'))
    
    # Run analysis
    data_analyzer.load_data(pbp_data)
    play_calling = data_analyzer.analyze_play_calling()
    run_outcomes = data_analyzer.analyze_play_outcomes(play_type='run')
    pass_outcomes = data_analyzer.analyze_play_outcomes(play_type='pass')
    
    # Export results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_exporter.export_csv(play_calling, f"play_calling_{timestamp}.csv")
    
    simulation_params = {
        "run_play": run_outcomes,
        "pass_play": pass_outcomes,
        "source_data": {
            "file": data_file,
            "timestamp": timestamp
        }
    }
    
    data_exporter.export_simulation_params(f"sim_params_{timestamp}.json")
    
    # Store in session for display
    results = {
        "play_calling": play_calling.to_dict() if not play_calling.empty else {},
        "run_outcomes": run_outcomes,
        "pass_outcomes": pass_outcomes
    }
    
    # In a real app, we'd store this properly, but for demo we'll use a file
    with open(os.path.join("results", f"analysis_results_{timestamp}.json"), 'w') as f:
        json.dump(results, f, indent=4)
    
    return redirect(url_for('analysis_results', analysis_id=timestamp))

@app.route('/analysis/results/<analysis_id>')
def analysis_results(analysis_id):
    """View analysis results."""
    # Load the results
    results_path = os.path.join("results", f"analysis_results_{analysis_id}.json")
    
    if not os.path.exists(results_path):
        flash('Analysis results not found', 'error')
        return redirect(url_for('analysis_data'))
    
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    return render_template('analysis/results.html', results=results, analysis_id=analysis_id)

@app.route('/season/setup', methods=['GET', 'POST'])
def season_setup():
    """Set up and run a season simulation."""
    teams = list(sim_engine.teams.keys()) if sim_engine.teams else []
    
    if request.method == 'POST':
        num_games = int(request.form.get('num_games', 4))
        
        # Run season simulation
        try:
            result = sim_engine.simulate_season(num_games_per_team=num_games, verbose=True)
            return redirect(url_for('season_results', season_id='latest'))
        except Exception as e:
            flash(f'Error simulating season: {str(e)}', 'error')
            return redirect(url_for('season_setup'))
    
    return render_template('simulation/season_setup.html', teams=teams)

@app.route('/season/results/<season_id>')
def season_results(season_id):
    """View season results."""
    # Similar to simulation_results, but for season data
    results_dir = "results"
    
    if season_id == 'latest':
        # Find the latest result file
        result_files = [f for f in os.listdir(results_dir) 
                         if f.endswith('.json') and f.startswith('season_results_')]
        
        if not result_files:
            flash('No season results found', 'error')
            return redirect(url_for('index'))
        
        # Sort by timestamp
        latest_file = sorted(result_files)[-1]
        
        # Load the results
        with open(os.path.join(results_dir, latest_file), 'r') as f:
            results = json.load(f)
        
        return render_template('simulation/season_results.html', results=results)
    else:
        flash('Specific season ID loading not implemented yet', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)